from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse


class GBParse:
    _params = {
        'page': 0,
    }

    def __init__(self, start_url):
        self.start_url = start_url
        self._url = urlparse(start_url)

    @staticmethod
    def get_soup(url: str, params: dict):
        response = requests.get(url, params=params)
        return BeautifulSoup(response.text, 'lxml')

    def get_post_links(self):
        all_links = []
        while True:
            self._params['page'] += 1
            soup = self.get_soup(self.start_url, self._params)
            page_soup_item = soup.find_all('div', attrs={'class': 'post-item'})
            if not page_soup_item:
                break
            for page_item in page_soup_item:
                item = page_item.findChildren('a', attrs={'class': 'post-item__title'})
                for link in item:
                    all_links.append(f'{self._url.scheme}://{self._url.hostname}{link.attrs["href"]}')
        return all_links

    def get_info_from_link(self):
        links = self.get_post_links()
        for link in links:
            soup = self.get_soup(link, params={})
            self.get_writer(soup)
            self.get_post(soup, link)
            self.get_tag(soup)

    def get_writer(self, post_soup):
        writer_info = post_soup.find('div', attrs={'class': 'row m-t'})
        writer = getattr(writer_info.find('div', attrs={'itemprop': 'author'}), 'text')
        writer_url = f'{self._url.scheme}://{self._url.hostname}{writer_info.contents[0].contents[0].attrs["href"]}'
        print(writer, writer_url, sep='\n')

    def get_post(self, post_soup, link):
        post_info = getattr(post_soup.find('h1', attrs={'class': 'blogpost-title'}), 'text')
        post_datetime = post_soup.find('time')['datetime']
        post_img = post_soup.find('img').attrs['src']
        post_link = link
        print(post_info, post_datetime, post_img, post_link, sep='\n')

    def get_tag(self, post_soup):
        all_tags = post_soup.findAll('a', attrs={'class': 'small'})
        for tag in all_tags:
            tag_name = getattr(tag, 'text')
            tag_url = f'{self._url.scheme}://{self._url.hostname}{tag.attrs["href"]}'
            print(tag_name, tag_url, sep='\n')

    def get_comment(self):
        pass


if __name__ == '__main__':
    gb_posts_url = 'https://geekbrains.ru/posts?page='
    gb = GBParse(gb_posts_url)
    gb.get_info_from_link()
