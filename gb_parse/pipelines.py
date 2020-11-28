# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem, CloseSpider


class GbparsePipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['gb_parse']

    def process_item(self, item, spider):
        collection = self.db[item.__class__.__name__]
        try:
            user_info = self.db.InstagramUser.find_one({'data.username': item['data']['username']})
            if not user_info:
                collection.insert_one(item)
                return item
            else:
                raise DropItem(f'The user already exists')
        except KeyError:
            try:
                path = item['path']
                if not item['start_user'] in path:
                    while not item['start_user'] in path:
                        next_point = self.db.InstagramParentItem.find_one({'user': path[0]})
                        path.appendleft(next_point['parent_user'])
                    item['path'] = list(path)
                    print(item['path'])
                    collection.insert_one(item)
                else:
                    raise CloseSpider(reason='Done')
            except KeyError:
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
