from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from insta_scraper.spiders.instagram import InstagramSpider
from insta_scraper import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider, parse_users=['iosifthecat', 'hardkea'])
    process.start()