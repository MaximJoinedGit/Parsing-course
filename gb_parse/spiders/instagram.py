import scrapy
import json
import datetime
from ..items import InstagramPosts, InstagramUser, InstagramUserFollow


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    query_hash = {
        'posts': '56a7068fea504063273cc2120ffd54f3',
        'tag_posts': '9b498c08113f1e09617a1703c22b2f32',
        'followers': 'c76146de99bb02f6415203be841dd25a',
        'following': 'd04b0a864b4b54837c0d870b0e77e076',
    }
    query_url = 'https://www.instagram.com/graphql/query/'

    def __init__(self, login, enc_password, *args, **kwargs):
        self.tags = ['python', 'time', 'sky']
        self.users = ['usual_flairs', 'nasa', 'nytimes']
        self.login = login
        self.enc_passwd = enc_password
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_post_item(edges):
        for node in edges:
            yield InstagramPosts(
                date_parse=datetime.datetime.now(),
                data=node['node']
            )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace('window._sharedData =', '')[:-1])

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.enc_passwd,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError:
            if response.json().get('authenticated'):
                # for tag in self.tags:
                    # yield response.follow(f'/explore/tags/{tag}/', callback=self.tag_parse)
                for user in self.users:
                    yield response.follow(f'/{user}/', callback=self.user_parse)

    def tag_parse(self, response):
        tag = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']

        yield InstagramPosts(
            date_parse=datetime.datetime.now(),
            data={
                'id': tag['id'],
                'name': tag['name'],
                'profile_pic_url': tag['profile_pic_url'],
            }
        )
        yield from self.get_tag_posts(tag, response)

    def tag_api_parse(self, response):
        yield from self.get_tag_posts(response.json()['data']['hashtag'], response)

    def get_tag_posts(self, tag, response):
        if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {
                'tag_name': tag['name'],
                'first': 100,
                'after': tag['edge_hashtag_to_media']['page_info']['end_cursor'],
            }
            url = f'{self.query_url}?query_hash={self.query_hash["tag_posts"]}&variables={json.dumps(variables)}'
            yield response.follow(url, callback=self.tag_api_parse)

        yield from self.get_post_item(tag['edge_hashtag_to_media']['edges'])

    def user_parse(self, response, **kwargs):
        user_data = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']
        yield InstagramUser(date_parse=datetime.datetime.now(),
                            data=user_data,
                            )
        yield from self.get_following_followers_api(response, user_data, self.query_hash['followers'],
                                                    'edge_followed_by')
        yield from self.get_following_followers_api(response, user_data, self.query_hash['following'], 'edge_follow')

    def get_following_followers_api(self, response, user_data, query_hash, edge, variables=None):
        if not variables:
            variables = {
                'id': user_data['id'],
                'first': 100,
            }
        api_url = f'{self.query_url}?query_hash={query_hash}&variables={json.dumps(variables)}'
        yield response.follow(api_url,
                              callback=self.following_and_followers_parse,
                              cb_kwargs={'user_data': user_data,
                                         'edge': edge,
                                         'query_hash': query_hash})

    def following_and_followers_parse(self, response, **kwargs):
        if b'application/json' in response.headers['Content-Type']:
            api_data = response.json()
            yield from self.following_or_followers_item(kwargs['user_data'], api_data['data']['user'], kwargs['edge'])
            if api_data['data']['user'][kwargs['edge']]['page_info']['has_next_page']:
                end_cursor = api_data['data']['user'][kwargs['edge']]['page_info']['end_cursor']
                variables = {
                    'id': kwargs['user_data']['id'],
                    'first': 100,
                    'after': end_cursor,
                }
                yield from self.get_following_followers_api(response, kwargs['user_data'], kwargs['query_hash'],
                                                            kwargs['edge'], variables)

    @staticmethod
    def following_or_followers_item(user_data, follow_data, edge):
        for user in follow_data[edge]['edges']:
            if edge == 'edge_followed_by' or edge == 'edge_follow':
                yield InstagramUserFollow(
                    user_id=user_data['id'],
                    user_name=user_data['username'],
                    follower_id=user['node']['id'],
                    follower_name=user['node']['username'],
                )
            else:
                pass
            yield InstagramUser(
                date_parse=datetime.datetime.now(),
                data=user['node'],
            )
