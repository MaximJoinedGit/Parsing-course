# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbparseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class HhVacanciesItem(scrapy.Item):
    _id = scrapy.Field()
    vacancy_name = scrapy.Field()
    vacancy_salary = scrapy.Field()
    vacancy_description = scrapy.Field()
    vacancy_skills = scrapy.Field()
    vacancy_author_url = scrapy.Field()


class HhEmployersItem(scrapy.Item):
    _id = scrapy.Field()
    employer_name = scrapy.Field()
    employer_url = scrapy.Field()
    employer_spec = scrapy.Field()
    employer_description = scrapy.Field()


class InstagramPosts(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    img = scrapy.Field()


class InstagramUser(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()


class InstagramUserFollow(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    follower_id = scrapy.Field()
    follower_name = scrapy.Field()
