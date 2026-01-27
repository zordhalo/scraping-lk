import os

# Scrapy settings for stitchy_lizard project

BOT_NAME = "stitchy_lizard"

SPIDER_MODULES = ["stitchy_lizard.spiders"]
NEWSPIDER_MODULE = "stitchy_lizard.spiders"

# Crawl responsibly by identifying yourself
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 0.5

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Override the default request headers
# DEFAULT_REQUEST_HEADERS = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#     "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# SPIDER_MIDDLEWARES = {
#     "stitchy_lizard.middlewares.StitchyLizardSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "scrapy_zyte_api.ScrapyZyteAPIDownloaderMiddleware": 1000,
}

# Enable or disable extensions
# EXTENSIONS = {
#     "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
ITEM_PIPELINES = {
    "scrapy.pipelines.images.ImagesPipeline": 1,
}

# Image pipeline settings
IMAGES_STORE = "product_images"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_CLASS = "scrapy_zyte_api.ScrapyZyteAPIRequestFingerprinter"

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

FEED_EXPORT_ENCODING = "utf-8"

# Zyte API Configuration
# The API key should be set via environment variable or Zyte Cloud project settings.
# NEVER hard-code the API key in this file.
ZYTE_API_KEY = os.environ.get("ZYTE_API_KEY", "")

# Enable Zyte API for all requests
ZYTE_API_ENABLED = True

# Use browser rendering for JavaScript-heavy pages (optional)
# ZYTE_API_BROWSER_HTML = True
