# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline


class GbparsePipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['gb_parse']

    def process_item(self, item, spider):
        collection = self.db[item.__class__.__name__]
        collection.insert_one(item)
        return item


class GbparseImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        images = item.get('img', item['data'].get('profile_pic_url', item['data'].get('display_url', [])))

        if not isinstance(images, list):
            images = [images]
        for url in images:
            try:
                yield Request(url)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        try:
            item['img'] = [itm[1] for itm in results if itm[0]]
        except KeyError:
            pass
        return item
