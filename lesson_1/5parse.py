import requests
import json
import time


class ParseFive:
    __params = {
        'categories': None,
    }

    __headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'
    }

    __url_discounts = 'https://5ka.ru/api/v2/special_offers/?store=&records_per_page=12&page=1&categories=&ordering=&' \
                      'price_promo__gte=&price_promo__lte=&search='

    def __init__(self, url_categories: str):
        self.url_categories = url_categories

    def parse(self, url=None):
        url = self.url_categories
        response_get_categories = requests.get(url, headers=self.__headers)
        params = self.__params
        for category in range(len(response_get_categories.json())):
            self.__params['categories'] = response_get_categories.json()[category]['parent_group_code']
            response_get_goods = requests.get(self.__url_discounts, params=params, headers=self.__headers)
            result_for_category = {'name': response_get_categories.json()[category]['parent_group_name'],
                                   'code': response_get_categories.json()[category]['parent_group_code'],
                                   'products': response_get_goods.json()["results"]}
            self.save_to_json(result_for_category)
            params = {}

    def save_to_json(self, result):
        with open(f'Products/{result["name"]}.json', 'w', encoding='utf-8') as file:
            json.dump(result, file, ensure_ascii=False)


if __name__ == '__main__':
    link = 'https://5ka.ru/api/v2/categories/'
    parser = ParseFive(link)
    parser.parse()
