# from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.loader import ItemLoader
from .items import HhVacanciesItem, HhEmployersItem


def get_author_url(itm):
    result = 'https://hh.ru' + itm
    return result


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
    # employer_name =
    # employer_url =
    # employer_spec =
    # employer_description =
