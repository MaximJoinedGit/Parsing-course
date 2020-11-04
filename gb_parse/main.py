from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse import settings
from gb_parse.spiders.youla import YoulaSpider
from gb_parse.spiders.hh import HhSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    # crawl_proc.crawl(YoulaSpider)
    crawl_proc.crawl(HhSpider)
    crawl_proc.start()
