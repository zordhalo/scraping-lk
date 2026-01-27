import scrapy


class ProductItem(scrapy.Item):
    """Item definition for Stitchy Lizard product data."""

    name = scrapy.Field()
    sku = scrapy.Field()
    url = scrapy.Field()
    sizes = scrapy.Field()
    min_order = scrapy.Field()
    colors = scrapy.Field()
    price_table = scrapy.Field()  # raw or parsed pricing tiers
    setup_charge = scrapy.Field()
    category = scrapy.Field()
    source = scrapy.Field()  # e.g. "stitchylizard.com"

    # Image fields for Scrapy's ImagesPipeline
    image_urls = scrapy.Field()  # List of image URLs to download
    images = scrapy.Field()  # Populated by ImagesPipeline with download results
