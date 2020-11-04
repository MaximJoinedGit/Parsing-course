import scrapy
from ..loaders import HhVacanciesLoader, HhEmployerLoader


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    vacancy_xpath = {
        'vacancy_name': '//h1[@data-qa="vacancy-title"]/text()',
        'vacancy_salary': '//p[@class="vacancy-salary"]//text()',
        'vacancy_description': '//div[@data-qa="vacancy-description"]//text()',
        'vacancy_skills': '//div[@class="bloko-tag-list"]//text()',
        'vacancy_author_url': '//a[@data-qa="vacancy-company-name"]/@href',
    }

    employer_xpath = {
        'employer_name': '//div[@class="sticky-container"]//h1[@class="bloko-header-1"]//text()',
        'employer_url': '//a[@data-qa="sidebar-company-site"]/@href',
        'employer_spec': '//div[@class="employer-sidebar-block"]//p/text()',
        'employer_description': '//div[@class="g-user-content"]//text()',
    }

    def parse(self, response, **kwargs):
        for url_pagination in response.xpath('//a[@data-qa="pager-next"]/@href'):
            yield response.follow(url_pagination, callback=self.parse)
        for url_vacancy in response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href'):
            yield response.follow(url_vacancy, callback=self.vacancy_parse)
        for url_employer in response.xpath('//a[@data-qa="vacancy-serp__vacancy-employer"]/@href'):
            yield response.follow(url_employer, callback=self.employer_parse)

    def vacancy_parse(self, response, **kwargs):
        vacancy_loader = HhVacanciesLoader(response=response)
        vacancy_loader.add_xpath('vacancy_name', self.vacancy_xpath['vacancy_name'])
        vacancy_loader.add_xpath('vacancy_salary', self.vacancy_xpath['vacancy_salary'])
        vacancy_loader.add_xpath('vacancy_description', self.vacancy_xpath['vacancy_description'])
        vacancy_loader.add_xpath('vacancy_skills', self.vacancy_xpath['vacancy_skills'])
        vacancy_loader.add_xpath('vacancy_author_url', self.vacancy_xpath['vacancy_author_url'])
        yield vacancy_loader.load_item()

    def employer_parse(self, response, **kwargs):
        employer_loader = HhEmployerLoader(response=response)
        employer_loader.add_xpath('employer_name', self.employer_xpath['employer_name'])
        employer_loader.add_xpath('employer_url', self.employer_xpath['employer_url'])
        employer_loader.add_xpath('employer_spec', self.employer_xpath['employer_spec'])
        employer_loader.add_xpath('employer_description', self.employer_xpath['employer_description'])
        yield employer_loader.load_item()
