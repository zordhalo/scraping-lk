# Scrapy settings for stitchylizard_scraper project

BOT_NAME = 'stitchylizard_scraper'

SPIDER_MODULES = ['stitchylizard_scraper.spiders']
NEWSPIDER_MODULE = 'stitchylizard_scraper.spiders'

# Respectful scraping
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 1.5  # Be polite - 1.5 second delay
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# User Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Enable cookies
COOKIES_ENABLED = True

# Enable pipelines
ITEM_PIPELINES = {
    'stitchylizard_scraper.pipelines.DataCleaningPipeline': 100,
    'stitchylizard_scraper.pipelines.ImageDownloadPipeline': 200,
}

# Image pipeline settings
IMAGES_STORE = 'output/images'
IMAGES_URLS_FIELD = 'image_urls'
IMAGES_RESULT_FIELD = 'images'
IMAGES_MIN_HEIGHT = 100
IMAGES_MIN_WIDTH = 100

# Output settings
FEEDS = {
    'output/data/products_%(time)s.json': {
        'format': 'json',
        'encoding': 'utf8',
        'indent': 2,
    },
    'output/data/products_%(time)s.csv': {
        'format': 'csv',
        'encoding': 'utf8',
    },
}

# Retry settings
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'output/scraper.log'

# Auto-throttle (adaptive delay)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
