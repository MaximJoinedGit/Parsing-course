from urllib.parse import urlparse
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests


class MagnitParser:
    _headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0',
    }
    _params = {
        'geo': 'moskva',
    }

    def __init__(self, start_url):
        self.start_url = start_url
        self._url = urlparse(start_url)
        mongo_client = MongoClient('mongodb://localhost:27017')
        self.db = mongo_client['parse_magnit']

    def _get_soup(self, url: str):
        response = requests.get(url, headers=self._headers)
        return BeautifulSoup(response.text, 'lxml')

    def parse(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})
        products = catalog.findChildren('a', attrs={'class': 'card-sale'})

        for product in products:
            if len(product.attrs.get('class')) > 2 or product.attrs.get('href')[0] != '/':
                continue
            product_url = f'{self._url.scheme}://{self._url.hostname}{product.attrs.get("href")}'
            product_soup = self._get_soup(product_url)
            product_data = self.get_product_structure(product_url, product_soup)
            self.save_to(product_data)

    def get_product_structure(self, url, product_soup):
        product_template = {
            'promo_name': ('p', 'action__name-text', 'text'),
            'product_name': ('div', 'action__title', 'text'),
            'old_price': ('div', 'label_big', 'label__price_old', 'text'),
            'new_price': ('div', 'label_big', 'label__price_new', 'text'),
            'image_url': ('img', 'action__image', 'data-src'),
            'date_from': ('div', 'action__date-label', 'text', 0),
            'date_to': ('div', 'action__date-label', 'text', 1),
        }
        product = {'url': url, }
        for keys in product_template.keys():
            if 'name' in keys:
                product[keys] = self.get_product_names(product_template[keys], product_soup)
            elif 'price' in keys:
                product[keys] = self.get_product_prices(product_template[keys], product_soup)
            elif 'image' in keys:
                product[keys] = self.get_product_image(product_template[keys], product_soup)
            elif 'date' in keys:
                product[keys] = self.get_product_dates(product_template[keys], product_soup)
        return product

    def get_product_names(self, name_structure: tuple, product_soup):
        try:
            name = getattr(
                product_soup.find(
                    name_structure[0],
                    attrs={'class': name_structure[1]}
                ),
                name_structure[2]
            )
            return name
        except Exception:
            name = None
            return name

    def get_product_prices(self, price_structure: tuple, product_soup):
        try:
            price = product_soup.find(
                price_structure[0],
                attrs={'class': price_structure[1]}
            ).find(
                price_structure[0],
                attrs={'class': price_structure[2]}
            ).text.replace('\n', '')
            return float(price) / 100
        except Exception:
            price = None
            return price

    def get_product_image(self, image_structure: tuple, product_soup):
        try:
            image_url = product_soup.find(image_structure[0], attrs={'class': image_structure[1]})[image_structure[2]]
            return f'{self._url.scheme}://{self._url.hostname}{image_url}'
        except Exception:
            image_url = None
            return image_url

    def get_product_dates(self, date_structure: tuple, product_soup):
        try:
            date = getattr(
                product_soup.find(
                    date_structure[0],
                    attrs={'class': date_structure[1]}
                ), date_structure[2]
            ).replace('с ', '').split(' по ')[date_structure[3]]
            return date
        except Exception:
            date = None
            return date

    def save_to(self, product_data: dict):
        collection = self.db['magnit']
        collection.insert_one(product_data)
        print('Item Done')


if __name__ == '__main__':
    url_magnit = 'https://magnit.ru/promo/?geo=moskva'
    parser = MagnitParser(url_magnit)
    parser.parse()
