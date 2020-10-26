from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
import gb_models
from bs4 import BeautifulSoup
import requests
import dateparser
from urllib.parse import urlparse

engine = create_engine('sqlite:///gb_blog.db')

gb_models.Base.metadata.create_all(bind=engine)

SessionMaker = sessionmaker(bind=engine)


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
            self.get_writer(soup, link)
            # self.get_post(soup, link)
            # self.get_tag(soup)

    def get_writer(self, post_soup, link):
        writer_info = post_soup.find('div', attrs={'class': 'row m-t'})
        writer = getattr(writer_info.find('div', attrs={'itemprop': 'author'}), 'text')
        writer_url = f'{self._url.scheme}://{self._url.hostname}{writer_info.contents[0].contents[0].attrs["href"]}'
        new_writer = db.query(gb_models.Writer).filter_by(url=writer_url)
        if not new_writer.value('id'):
            writer_add = gb_models.Writer(name=writer, url=writer_url)
            db.add(writer_add)
            print(f'Item {writer} done')
        post_info = getattr(post_soup.find('h1', attrs={'class': 'blogpost-title'}), 'text')
        post_datetime = dateparser.parse(post_soup.find('time')['datetime'])
        post_img = post_soup.find('img').attrs['src']
        post_link = link
        post_writer_id = db.query(gb_models.Writer).filter_by(url=writer_url)
        new_post = db.query(gb_models.Post).filter_by(url=post_link)
        if not new_post.value('id'):
            post_add = gb_models.Post(url=post_link, header=post_info, date=post_datetime, img_url=post_img,
                                      writer_id=post_writer_id.value('id'))
            db.add(post_add)
            print(f'Item post "{post_info}" done')
        all_tags = post_soup.findAll('a', attrs={'class': 'small'})
        for tag in all_tags:
            tag_name = getattr(tag, 'text')
            tag_url = f'{self._url.scheme}://{self._url.hostname}{tag.attrs["href"]}'
            new_tag = db.query(gb_models.Tag).filter_by(url=tag_url)
            if not new_tag.value('id'):
                tag_add = gb_models.Tag(name=tag_name, url=tag_url)
                db.add(tag_add)
                print(f'Item {tag_name} done')
            tag_post_query = insert(gb_models.tag_post).values(post_id=new_post.value('id'), tag_id=new_tag.value('id'))
            db.execute(tag_post_query)
        db.commit()

    def get_comment(self):
        pass


if __name__ == '__main__':
    db = SessionMaker()
    gb_posts_url = 'https://geekbrains.ru/posts?page='
    gb_parse = GBParse(gb_posts_url)
    gb_parse.get_info_from_link()
