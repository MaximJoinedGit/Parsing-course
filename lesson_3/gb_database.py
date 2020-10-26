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

    _comment_link = 'https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id=&order=desc'

    _params = {
        'page': 0,
    }

    def __init__(self, start_url):
        self.start_url = start_url
        self._url = urlparse(start_url)
        self.writer_url = None
        self.new_post = None

    @staticmethod
    def get_soup(url: str, params: dict):
        """
        Получает на вход url, делает суп.
        """
        response = requests.get(url, params=params)
        return BeautifulSoup(response.text, 'lxml')

    def get_post_links(self):
        """
        Обходит все страницы в блоге, получает ссылки на посты.
        """
        while True:
            self._params['page'] += 1
            soup = self.get_soup(self.start_url, self._params)
            page_soup_item = soup.find_all('div', attrs={'class': 'post-item'})
            if not page_soup_item:
                break
            for page_item in page_soup_item:
                item = page_item.findChildren('a', attrs={'class': 'post-item__title'})
                for link in item:
                    link = f'{self._url.scheme}://{self._url.hostname}{link.attrs["href"]}'
                    yield link

    def parse_gb(self):
        """
        Парсит страницы, полученные в get_post_links.
        """
        links = self.get_post_links()
        for link in links:
            soup = self.get_soup(link, params={})
            self.fill_writer_table(soup)
            self.fill_post_table(soup, link)
            self.fill_tag_post_tag_tables(soup)
            self.fill_comments_table(soup, link)

    def fill_writer_table(self, post_soup):
        """
        Заполняет таблицу Writer.
        """
        writer_info = post_soup.find('div', attrs={'class': 'row m-t'})
        writer_name = getattr(writer_info.find('div', attrs={'itemprop': 'author'}), 'text')
        self.writer_url = f'{self._url.scheme}://' \
                          f'{self._url.hostname}{writer_info.contents[0].contents[0].attrs["href"]}'
        new_writer = db.query(gb_models.Writer).filter_by(url=self.writer_url)
        if not new_writer.value('id'):
            writer_add = gb_models.Writer(name=writer_name, url=self.writer_url)
            db.add(writer_add)
            print(f'{writer_name} добавлен')

    def fill_post_table(self, post_soup, link):
        """
        Заполняет страницу Post.
        """
        post_info = getattr(post_soup.find('h1', attrs={'class': 'blogpost-title'}), 'text')
        post_datetime = dateparser.parse(post_soup.find('time')['datetime'])
        post_img = post_soup.find('img').attrs['src']
        post_writer_id = db.query(gb_models.Writer).filter_by(url=self.writer_url)
        self.new_post = db.query(gb_models.Post).filter_by(url=link)
        if not self.new_post.value('id'):
            post_add = gb_models.Post(url=link, header=post_info, date=post_datetime, img_url=post_img,
                                      writer_id=post_writer_id.value('id'))
            db.add(post_add)
            print(f'Статья "{post_info}" добавлена')

    def fill_tag_post_tag_tables(self, post_soup):
        """
        Заполняет таблицы Tag и tag_post.
        """
        all_tags = post_soup.findAll('a', attrs={'class': 'small'})
        for tag in all_tags:
            tag_name = getattr(tag, 'text')
            tag_url = f'{self._url.scheme}://{self._url.hostname}{tag.attrs["href"]}'
            new_tag = db.query(gb_models.Tag).filter_by(url=tag_url)
            if not new_tag.value('id'):
                tag_add = gb_models.Tag(name=tag_name, url=tag_url)
                db.add(tag_add)
                print(f'Тэг {tag_name} добавлен')
            tag_post_query = insert(gb_models.tag_post).values(post_id=self.new_post.value('id'),
                                                               tag_id=new_tag.value('id'))
            db.execute(tag_post_query)
        db.commit()

    def fill_comments_table(self, post_soup, link):
        """
        Заполняет таблицу Comment.
        """
        page_id = post_soup.find('div', attrs={'class': 'm-t-lg'}).findChild('div')['data-minifiable-id']
        comment_params = {'commentable_id': page_id}
        comments = requests.get(self._comment_link, params=comment_params)
        if not comments.json() == []:
            for comment in range(len(comments.json())):
                comment_text = comments.json()[comment]['comment']['body']
                comment_writer_url = comments.json()[0]['comment']['user']['url']
                comment_writer = comments.json()[0]['comment']['user']['full_name']
                writer_exists = db.query(gb_models.Writer).filter_by(url=comment_writer_url)
                post_comment_id = db.query(gb_models.Post).filter_by(url=link)
                while not writer_exists.value('id'):
                    writer_add = gb_models.Writer(name=comment_writer, url=comment_writer_url)
                    db.add(writer_add)
                    print(f'{comment_writer} добавлен')
                    db.commit()
                    writer_exists = db.query(gb_models.Writer).filter_by(url=comment_writer_url)
                if writer_exists:
                    comment_add = gb_models.Comment(text=comment_text, writer_id=writer_exists.value('id'),
                                                    post_id=post_comment_id.value('id'))
                    db.add(comment_add)
                    print(f'Добавлен комментарий {comment_text}')
                    db.commit()


if __name__ == '__main__':
    db = SessionMaker()
    gb_posts_url = 'https://geekbrains.ru/posts?page='
    gb_parse = GBParse(gb_posts_url)
    gb_parse.parse_gb()
