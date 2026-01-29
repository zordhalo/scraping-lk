import re
import scrapy
from datetime import datetime
from stitchylizard_scraper.items import ProductItem


class ProductsSpider(scrapy.Spider):
    name = 'products'
    allowed_domains = ['stitchylizard.com']

    # Define all category URLs to scrape
    start_urls_config = {
        # APPAREL
        'tshirts': '/custom-apparel/t-shirts.html',
        'sweatshirts': '/custom-apparel/sweatshirts.html',
        'hoodies': '/custom-apparel/sweatshirts.html',
        'jackets': '/custom-apparel/jackets.html',

        # BAGS
        'tote_bags': '/custom-bags/tote-bags.html',
        'drawstring_bags': '/custom-bags/drawstring-bags.html',

        # DRINKWARE
        'water_bottles': '/custom-drinkware-toronto/water-bottles.html',
        'mugs': '/custom-drinkware-toronto/mugs.html',

        # PRINT
        'business_cards': '/custom-print-toronto/custom-business-cards.html',
        'brochures': '/custom-print-toronto.html',
        'posters': '/custom-print-toronto.html',
        'banners': '/custom-print-toronto.html',

        # PROMOTIONAL
        'keychains': '/custom-promo-products/promotional-k-l/key-chains.html',
        'pens': '/custom-promo-products/promotional-m-r/pens.html',
        'signage': '/custom-promo-products/promotional-s-z/signs.html',
    }

    base_url = 'https://stitchylizard.com'

    def start_requests(self):
        for category, path in self.start_urls_config.items():
            url = self.base_url + path
            yield scrapy.Request(
                url=url,
                callback=self.parse_category,
                meta={'category': category}
            )

    def parse_category(self, response):
        """Parse category listing page and handle pagination"""
        category = response.meta['category']

        # Extract product links from listing page
        product_links = response.css('a.product-item-link::attr(href)').getall()

        # Alternative selectors based on site structure
        if not product_links:
            product_links = response.css('.product-item a::attr(href)').getall()
        if not product_links:
            product_links = response.xpath(
                '//a[contains(@href, ".html") and ancestor::div[contains(@class, "product")]]/@href'
            ).getall()

        for link in product_links:
            if link and '.html' in link:
                full_url = response.urljoin(link)
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_product,
                    meta={'category': category}
                )

        # Handle pagination
        next_page = response.css('a.action.next::attr(href)').get()
        if not next_page:
            next_page = response.xpath('//a[contains(@class, "next")]/@href').get()

        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse_category,
                meta={'category': category}
            )

    def parse_product(self, response):
        """Parse individual product page"""
        item = ProductItem()

        # Basic Info
        item['name'] = response.css('h1.page-title span::text').get() or \
                       response.css('h1::text').get()
        item['name'] = item['name'].strip() if item['name'] else ''

        item['sku'] = response.css('.product-info-main .sku .value::text').get() or \
                      response.xpath('//span[contains(text(), "SKU")]/following-sibling::text()').get()

        item['url'] = response.url
        item['category'] = response.meta['category']

        # Extract subcategory from breadcrumbs
        breadcrumbs = response.css('.breadcrumbs li a::text').getall()
        item['subcategory'] = breadcrumbs[-1] if breadcrumbs else ''

        # Pricing Table
        item['pricing_table'] = self.extract_pricing(response)

        # Setup charges
        setup_text = response.xpath(
            '//*[contains(text(), "Setup Charge")]/following-sibling::text()'
        ).get()
        item['setup_charge'] = self.clean_price(setup_text)

        # Additional location charge
        location_text = response.xpath(
            '//*[contains(text(), "Additional Location")]/following-sibling::text()'
        ).get()
        item['additional_location_charge'] = self.clean_price(location_text)

        # Description
        item['description'] = ' '.join(
            response.css('#description *::text').getall()
        ).strip()
        if not item['description']:
            item['description'] = ' '.join(
                response.css('.product-info-main .value *::text').getall()
            ).strip()

        # Sizes
        sizes_text = response.xpath(
            '//*[contains(text(), "Sizes")]/following-sibling::text()'
        ).get()
        item['sizes'] = sizes_text.strip() if sizes_text else ''

        # Colors - extract from color swatches or text
        colors = response.css('.swatch-option::attr(aria-label)').getall()
        if not colors:
            colors_text = response.xpath(
                '//*[contains(text(), "colours") or contains(text(), "colors")]/text()'
            ).get()
            item['colors'] = colors_text if colors_text else colors
        else:
            item['colors'] = colors

        # Minimum Order
        min_order_text = response.xpath(
            '//*[contains(text(), "Minimum Order")]/following-sibling::text()'
        ).get()
        item['minimum_order'] = min_order_text.strip() if min_order_text else ''

        # Production Time
        prod_time = response.xpath(
            '//*[contains(text(), "Production time")]/text()'
        ).get()
        item['production_time'] = prod_time.strip() if prod_time else ''

        # Images - collect all product images
        image_urls = []

        # Main product images
        main_images = response.css('.fotorama__img::attr(src)').getall()
        image_urls.extend(main_images)

        # Gallery images
        gallery_images = response.css('.gallery-placeholder img::attr(src)').getall()
        image_urls.extend(gallery_images)

        # Data-src images (lazy loaded)
        lazy_images = response.css('img[data-src]::attr(data-src)').getall()
        image_urls.extend(lazy_images)

        # Full-size image links
        full_images = response.css('a.fotorama__img::attr(href)').getall()
        image_urls.extend(full_images)

        # Remove duplicates and filter valid URLs
        item['image_urls'] = list(set([
            response.urljoin(url) for url in image_urls
            if url and ('.jpg' in url.lower() or '.png' in url.lower() or '.webp' in url.lower())
        ]))

        item['thumbnail_url'] = item['image_urls'][0] if item['image_urls'] else ''

        # Manufacturer
        item['manufacturer'] = response.css('.product-brand::text').get() or ''

        # Metadata
        item['scraped_at'] = datetime.now().isoformat()

        yield item

    def extract_pricing(self, response):
        """Extract pricing table from product page"""
        pricing = {}

        # Look for pricing table rows
        table_rows = response.css('table tr')

        for row in table_rows:
            cells = row.css('td::text').getall()
            if len(cells) >= 2:
                try:
                    quantity = cells[0].strip()
                    price = cells[1].strip()
                    if quantity.isdigit():
                        pricing[quantity] = price
                except Exception:
                    continue

        # Alternative: Look for quantity/price pairs in text
        if not pricing:
            qty_elements = response.xpath(
                '//*[contains(@class, "qty") or contains(@class, "quantity")]//text()'
            ).getall()
            price_elements = response.xpath(
                '//*[contains(@class, "price")]//text()'
            ).getall()

            for i, qty in enumerate(qty_elements):
                if i < len(price_elements):
                    pricing[qty.strip()] = price_elements[i].strip()

        return pricing

    def clean_price(self, text):
        """Clean and format price string"""
        if not text:
            return ''
        match = re.search(r'[\d.,]+', text)
        return match.group() if match else text.strip()
