import scrapy
from pymongo import MongoClient


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
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
        description = response.xpath(self.xpath['description']).extract_first().replace('\n', '. ')

        # Страница продавца
        # seller_url = response.xpath('//div[contains(@class, "SellerInfo_block")]')

        # Список ключей для характеристик
        specs_list_keys = response.xpath(self.xpath['specs_keys']).getall()

        # Список значений для характеристик
        specs_list_values = response.xpath(self.xpath['specs_values']).getall()

        specs_list = dict(zip(specs_list_keys, specs_list_values))

        # Соранение в БД
        collection = self.db_client['parse_magnit'][self.name]
        collection.insert_one({'title': name, 'img': images, 'description': description, 'Specs': specs_list})
