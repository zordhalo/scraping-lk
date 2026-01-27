import scrapy

from stitchy_lizard.items import ProductItem


class StitchyLizardSpider(scrapy.Spider):
    """Spider for scraping product data from stitchylizard.com."""

    name = "stitchy_lizard"
    allowed_domains = ["stitchylizard.com", "cdn.stitchylizard.com"]
    start_urls = [
        "https://stitchylizard.com/custom-apparel/t-shirts/short-sleeve.html",
        "https://stitchylizard.com/custom-apparel/custom-sweatshirts.html",
        "https://stitchylizard.com/custom-apparel/custom-printed-jackets.html",
        "https://stitchylizard.com/custom-bags/tote-bags.html",
        "https://stitchylizard.com/custom-bags/drawstring-bags.html",
        "https://stitchylizard.com/custom-drinkware-toronto/water-bottles.html",
        "https://stitchylizard.com/custom-drinkware-toronto/mugs.html",
        "https://stitchylizard.com/custom-print-toronto/custom-business-cards.html",
        "https://stitchylizard.com/custom-promo-products/promo-d-l/custom-printed-key-chains.html",
        "https://stitchylizard.com/custom-promo-products/promo-m-r/custom-pens-toronto.html",
    ]

    def parse(self, response):
        """Parse category/listing pages and follow product links."""
        # Extract product links from listing pages
        # Look for product links in common patterns
        for product in response.css("h2 a[href$='.html']"):
            href = product.attrib.get("href")
            if href:
                yield response.follow(href, self.parse_product)

        # Alternative selectors for product links
        for product in response.css(".product-item a[href$='.html']::attr(href)").getall():
            yield response.follow(product, self.parse_product)

        for product in response.css(".product-name a[href$='.html']::attr(href)").getall():
            yield response.follow(product, self.parse_product)

        # Handle pagination
        for page in response.css("a[href*='?p=']::attr(href)").getall():
            yield response.follow(page, self.parse)

        # Alternative pagination patterns
        for page in response.css(".pages a::attr(href)").getall():
            yield response.follow(page, self.parse)

    def parse_product(self, response):
        """Parse individual product pages and extract product data."""
        item = ProductItem()

        # Basic product info
        item["name"] = self._extract_text(response.css("h1::text"))
        item["url"] = response.url
        item["source"] = "stitchylizard.com"

        # SKU extraction - try multiple patterns
        item["sku"] = self._extract_sku(response)

        # Sizes
        item["sizes"] = self._extract_field(response, "Sizes")

        # Minimum order quantity
        item["min_order"] = self._extract_field(response, "Minimum Order Quantity")

        # Colors/Available in
        item["colors"] = self._extract_field(response, "Available in")

        # Setup charge
        item["setup_charge"] = self._extract_setup_charge(response)

        # Category from breadcrumbs
        item["category"] = self._extract_category(response)

        # Price table
        item["price_table"] = self._extract_price_table(response)

        # Images - for Scrapy's ImagesPipeline
        item["image_urls"] = self._extract_images(response)

        yield item

    def _extract_text(self, selector, default=""):
        """Extract and clean text from a selector."""
        text = selector.get(default=default)
        return text.strip() if text else default

    def _extract_sku(self, response):
        """Extract SKU using multiple selector patterns."""
        # Try various patterns
        patterns = [
            '//text()[contains(., "Sku:")]/following-sibling::text()[1]',
            '//span[contains(text(), "Sku")]/following-sibling::text()[1]',
            '//td[contains(text(), "Sku")]/following-sibling::td/text()',
            '//*[contains(@class, "sku")]/text()',
        ]
        for pattern in patterns:
            result = response.xpath(pattern).get()
            if result and result.strip():
                return result.strip()

        # CSS fallback
        sku = response.css(".sku::text, .product-sku::text").get()
        return sku.strip() if sku else ""

    def _extract_field(self, response, field_name):
        """Extract a field value by its label."""
        # XPath patterns
        patterns = [
            f'//text()[contains(., "{field_name}")]/../text()',
            f'//td[contains(text(), "{field_name}")]/following-sibling::td/text()',
            f'//span[contains(text(), "{field_name}")]/following-sibling::span/text()',
            f'//*[contains(text(), "{field_name}")]/following-sibling::*/text()',
        ]
        for pattern in patterns:
            result = response.xpath(pattern).get()
            if result and result.strip():
                return result.strip()
        return ""

    def _extract_setup_charge(self, response):
        """Extract setup charge from product page."""
        patterns = [
            '//text()[contains(., "Setup Charge")]/../following-sibling::td/text()',
            '//td[contains(text(), "Setup")]/following-sibling::td/text()',
            '//*[contains(text(), "Setup Charge")]/following-sibling::*/text()',
        ]
        for pattern in patterns:
            result = response.xpath(pattern).get()
            if result and result.strip():
                return result.strip()
        return ""

    def _extract_category(self, response):
        """Extract category from breadcrumbs."""
        # Try various breadcrumb patterns
        category = response.xpath(
            '//div[@class="breadcrumbs"]//li[last()]/strong/text()'
        ).get()
        if category:
            return category.strip()

        category = response.css(".breadcrumbs li:last-child::text").get()
        if category:
            return category.strip()

        category = response.css(".breadcrumb li:last-child a::text").get()
        if category:
            return category.strip()

        return ""

    def _extract_price_table(self, response):
        """Extract pricing table data."""
        price_rows = []

        # Try to find pricing tables
        for table in response.css("table"):
            rows = []
            for row in table.css("tr"):
                cols = [c.strip() for c in row.css("td::text, th::text").getall() if c.strip()]
                if cols:
                    rows.append(cols)
            if rows:
                price_rows.extend(rows)

        return price_rows if price_rows else []

    def _extract_images(self, response):
        """Extract all product images: main, gallery, and color variants."""
        image_urls = []

        # 1. Main product image (img#image-main)
        main_img = response.css("img#image-main::attr(src)").get()
        if main_img:
            image_urls.append(response.urljoin(main_img))

        # 2. Gallery thumbnail images (img#galleryChanger)
        gallery_imgs = response.css("img#galleryChanger::attr(src)").getall()
        for img in gallery_imgs:
            if img:
                image_urls.append(response.urljoin(img))

        # 3. Color variant images from swatches (high-res CDN images)
        # Selector: ul[id^="ul_swatch"] a[href*="cdn.stitchylizard.com"]
        color_imgs = response.css('ul[id^="ul_swatch_"] a::attr(href)').getall()
        for img in color_imgs:
            if img and "cdn.stitchylizard.com" in img:
                image_urls.append(img)

        # Alternative: any CDN images in swatch links
        swatch_imgs = response.css('a[href*="cdn.stitchylizard.com"]::attr(href)').getall()
        for img in swatch_imgs:
            if img and img not in image_urls:
                image_urls.append(img)

        # Deduplicate while preserving order
        seen = set()
        unique_urls = []
        for url in image_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        return unique_urls
