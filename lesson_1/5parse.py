import requests
import json
import time


class ParseFive:
    _params = {
        'categories': None,
    }

    _headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'
    }

    def __init__(self, url_categories: str):
        self.url_categories = url_categories

    @staticmethod
    def _get(*args, **kwargs):
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    raise Exception
                time.sleep(0.1)
                return response
            except Exception:
                time.sleep(0.250)

    def parse(self, url=None):
        url = self.url_categories
        response_get_categories = self._get(url, headers=self._headers)
        params = self._params
        for category in range(len(response_get_categories.json())):
            params['categories'] = response_get_categories.json()[category]['parent_group_code']
            url_discounts = 'https://5ka.ru/api/v2/special_offers/?store=&records_per_page=12&page=1&categories=&' \
                            'ordering=&price_promo__gte=&price_promo__lte=&search='
            results = []
            while url_discounts:
                response_get_goods = self._get(url_discounts, params=params, headers=self._headers)
                results.extend(response_get_goods.json()["results"])
                url_discounts = response_get_goods.json()['next']
            result_for_category = {'name': response_get_categories.json()[category]['parent_group_name'],
                                   'code': response_get_categories.json()[category]['parent_group_code'],
                                   'products': results}
            self.save_to_json(result_for_category)
            params = {}

    def save_to_json(self, result):
        with open(f'Products/{result["name"].lower().replace(" ", "_").replace(".", "_").replace(",", "_")}.json', 'w',
                  encoding='utf-8') as file:
            json.dump(result, file, ensure_ascii=False)
        # print('Item done')


if __name__ == '__main__':
    link = 'https://5ka.ru/api/v2/categories/'
    parser = ParseFive(link)
    parser.parse()
