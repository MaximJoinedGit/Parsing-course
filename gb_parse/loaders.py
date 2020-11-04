# from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.loader import ItemLoader
from .items import HhVacanciesItem, HhEmployersItem


def get_author_url(itm):
    return 'https://hh.ru' + itm


def get_employer_specs(itm):
    return itm


class HhVacanciesLoader(ItemLoader):
    default_item_class = HhVacanciesItem
    vacancy_name_out = TakeFirst()
    vacancy_salary_in = ''.join
    vacancy_salary_out = TakeFirst()
    vacancy_description_in = ''.join
    vacancy_description_out = TakeFirst()
    vacancy_skills_in = ''.join
    vacancy_skills_out = TakeFirst()
    vacancy_author_url_in = MapCompose(get_author_url)
    vacancy_author_url_out = TakeFirst()


class HhEmployerLoader(ItemLoader):
    default_item_class = HhEmployersItem
    employer_name_in = ''.join
    employer_name_out = TakeFirst()
    employer_url_out = TakeFirst()
    employer_spec_out = MapCompose(get_employer_specs)
    employer_description_in = ''.join
    employer_description_out = TakeFirst()
