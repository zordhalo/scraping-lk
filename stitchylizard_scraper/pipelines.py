import hashlib
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


class DataCleaningPipeline:
    """Clean and validate scraped data"""

    def process_item(self, item, spider):
        # Validate required fields
        if not item.get('name') or not item.get('sku'):
            raise DropItem(f"Missing name or SKU: {item}")

        # Clean text fields
        for field in ['name', 'description', 'sizes', 'minimum_order']:
            if item.get(field):
                item[field] = ' '.join(item[field].split())  # Normalize whitespace

        # Ensure pricing is dict
        if not isinstance(item.get('pricing_table'), dict):
            item['pricing_table'] = {}

        return item


class ImageDownloadPipeline(ImagesPipeline):
    """Custom image pipeline with organized folder structure"""

    def get_media_requests(self, item, info):
        for image_url in item.get('image_urls', []):
            yield Request(
                image_url,
                meta={
                    'category': item.get('category', 'misc'),
                    'sku': item.get('sku', 'unknown'),
                    'item': item,
                }
            )

    def file_path(self, request, response=None, info=None, *, item=None):
        """Organize images by category/sku/filename"""
        category = request.meta.get('category', 'misc')
        sku = request.meta.get('sku', 'unknown')

        # Clean SKU for folder name
        sku_clean = "".join(c for c in sku if c.isalnum() or c in '-_')

        # Generate unique filename from URL
        image_guid = hashlib.sha1(request.url.encode()).hexdigest()

        # Get file extension from URL
        url_path = request.url.split('?')[0]
        extension = url_path.split('.')[-1].lower()
        if extension not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
            extension = 'jpg'

        return f'{category}/{sku_clean}/{image_guid}.{extension}'

    def item_completed(self, results, item, info):
        """Handle completed image downloads"""
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths and item.get('image_urls'):
            # Log warning but don't drop item
            info.spider.logger.warning(
                f"Could not download any images for item: {item.get('sku')}"
            )
        item['images'] = image_paths
        return item
