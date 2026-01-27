# Stitchy Lizard Scraper

A Scrapy project for scraping product data from [stitchylizard.com](https://stitchylizard.com), designed to run on Zyte Cloud (Scrapy Cloud) with Zyte API integration.

## Project Structure

```
zyte/
  scrapy.cfg
  requirements.txt
  stitchy_lizard/
    __init__.py
    items.py
    middlewares.py
    pipelines.py
    settings.py
    spiders/
      __init__.py
      stitchy_spider.py
```

## Features

- Scrapes product data from multiple Stitchy Lizard categories
- Extracts: name, SKU, URL, sizes, minimum order, colors, pricing tables, setup charges
- Integrated with Zyte API via `scrapy-zyte-api` for reliable fetching
- Ready for deployment to Zyte Cloud

## Local Development

### Installation

```bash
pip install -r requirements.txt
```

### Running Locally

For local development without Zyte API:

```bash
scrapy crawl stitchy_lizard -o products.json
```

To run locally with Zyte API (requires API key):

```bash
export ZYTE_API_KEY="your-api-key-here"
scrapy crawl stitchy_lizard -o products.json
```

## Zyte Cloud Deployment

### 1. Connect GitHub Repository

1. Log in to [Zyte Cloud](https://app.zyte.com/)
2. Create a new project or select an existing one
3. Go to **Deploy** > **Deploy from GitHub**
4. Connect to `zordhalo/zyte` repository
5. Select the branch to deploy (e.g., `main`)

### 2. Configure API Key

1. In Zyte Cloud, go to **Project Settings** > **Settings**
2. Add `ZYTE_API_KEY` as an environment variable with your Zyte API key
3. The spider will automatically use this key via the `scrapy-zyte-api` middleware

**Important:** Never commit your API key to the repository.

### 3. Run the Spider

1. Go to **Spiders** in your Zyte Cloud project
2. Select `stitchy_lizard`
3. Click **Run**
4. Download results as JSON/CSV from the job page

### 4. Schedule Periodic Jobs

1. Go to **Periodic Jobs** in Zyte Cloud
2. Create a new periodic job for `stitchy_lizard`
3. Set your desired schedule (e.g., daily, weekly)

## Scraped Data Fields

| Field | Description |
|-------|-------------|
| `name` | Product name |
| `sku` | Product SKU/code |
| `url` | Product page URL |
| `sizes` | Available sizes |
| `min_order` | Minimum order quantity |
| `colors` | Available colors |
| `price_table` | Pricing tiers (list of rows) |
| `setup_charge` | Setup/printing charges |
| `category` | Product category from breadcrumbs |
| `source` | Source website (stitchylizard.com) |

## Categories Scraped

- Custom Apparel: T-shirts, Sweatshirts, Jackets
- Custom Bags: Tote Bags, Drawstring Bags
- Custom Drinkware: Water Bottles, Mugs
- Custom Print: Business Cards
- Promo Products: Key Chains, Pens

## Configuration

Key settings in [stitchy_lizard/settings.py](stitchy_lizard/settings.py):

- `CONCURRENT_REQUESTS`: 8 (parallel requests)
- `DOWNLOAD_DELAY`: 0.5 seconds (rate limiting)
- `ROBOTSTXT_OBEY`: True (respects robots.txt)
- `ZYTE_API_ENABLED`: True (uses Zyte API for all requests)

## License

Private project for internal use.
