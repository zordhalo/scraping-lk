import scrapy


class ProductItem(scrapy.Item):
    # Basic Info
    name = scrapy.Field()
    sku = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()

    # Pricing
    pricing_table = scrapy.Field()  # Dict with quantity: price
    setup_charge = scrapy.Field()
    additional_location_charge = scrapy.Field()

    # Product Details
    description = scrapy.Field()
    sizes = scrapy.Field()
    colors = scrapy.Field()
    minimum_order = scrapy.Field()
    production_time = scrapy.Field()

    # Images
    image_urls = scrapy.Field()      # For ImagesPipeline
    images = scrapy.Field()          # Downloaded image info
    thumbnail_url = scrapy.Field()

    # Metadata
    manufacturer = scrapy.Field()
    scraped_at = scrapy.Field()
