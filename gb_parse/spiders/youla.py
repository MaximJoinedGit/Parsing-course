import scrapy
from pymongo import MongoClient
from re import findall, compile


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/moskva']
    xpath = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'ads': '//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]/a/@href',
        'name': '//div[contains(@class, "AdvertCard_advertTitle")]/text()',
        'images': '//div[contains(@class, "PhotoGallery_block")]//img/@src',
        'description': '//div[@data-target="advert-info-descriptionFull"]/text()',
        'specs_keys': '//div[contains(@class, "AdvertCard_specs")]//div[contains(@class, "AdvertSpecs_label")]/text()',
        'specs_values':
            '//div[contains(@class, "AdvertCard_specs")]//div[contains(@class, "AdvertSpecs_data")]//text()',
        'script': '//script[contains(text(), "window.transitState =")]/text()',
    }
    db_client = MongoClient('mongodb://localhost:27017')

    def parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['brands']):
            yield response.follow(url, callback=self.brand_parse)

    def brand_parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.brand_parse)
        for url in response.xpath(self.xpath['ads']):
            yield response.follow(url, callback=self.ads_parse)

    def ads_parse(self, response, **kwargs):

        # Название
        name = response.xpath(self.xpath['name']).extract_first()

        # Картинки
        images = response.xpath(self.xpath['images']).extract()

        # Описание
        description = response.xpath(self.xpath['description']).extract_first()
        if description and '\n' in description:
            description.replace('\n', '')

        # Страница продавца
        seller_url = self.js_decoder_author(response)

        # Список ключей для характеристик
        specs_list_keys = response.xpath(self.xpath['specs_keys']).getall()

        # Список значений для характеристик
        specs_list_values = response.xpath(self.xpath['specs_values']).getall()

        specs_list = dict(zip(specs_list_keys, specs_list_values))

        # Соранение в БД
        collection = self.db_client['gb_parse'][self.name]
        collection.insert_one({'title': name,
                               'img': images,
                               'description': description,
                               'Specs': specs_list,
                               'author': seller_url,
                               })

    def js_decoder_author(self, response):
        script = response.xpath(self.xpath['script']).get()
        find_id = compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
        result = findall(find_id, script)
        return f'https://youla.ru/user/{result[0]}' if result else None
