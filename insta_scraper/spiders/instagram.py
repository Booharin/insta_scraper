import scrapy
from scrapy.http import HtmlResponse
import json
import re
from urllib.parse import urlencode
from copy import deepcopy
from insta_scraper.items import InstaScraperItem, FollowerItem


class InstagramSpider(scrapy.Spider):

    def __init__(self, parse_users):
        self.parse_users = parse_users

    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    insta_login = 'sladkieshtuchki'
    insta_pass = '#PWD_INSTAGRAM_BROWSER:10:1594988754:ATlQAO9GwG9/a+wwraWMKgoOjBqRW4YnTFDvJKED1OMsT60JMyhwvEn8CChz0B+G4U9N3Bij5cAEhhjajMfZXuU37iCBInJo+iTdSzyvVj9w6BvpHoDC3ZBR/0g40NIGwUfMYqyrn6smLEPB'
    insta_login_link = 'http://instagram.com/accounts/login/ajax/'
    # hashes
    post_hash = '15bf78a4ad24e33cbd838fdb31353ac1'
    followers_hash = 'c76146de99bb02f6415203be841dd25a'

    graphql_url = 'https://www.instagram.com/graphql/query/?'

    def parse(self, response: HtmlResponse):
        yield scrapy.FormRequest(
            self.insta_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login,
                      'enc_password': self.insta_pass},
            headers={'X-CSRFToken':self.fetch_csrf_token(response.text)}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.parse_users:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {"id": user_id,
                     "first": 50}
        # posts
        # url_posts = f'{self.graphql_url}query_hash={self.post_hash}&{urlencode(variables)}'
        # yield response.follow(
        #     url_posts,
        #     callback=self.user_posts_parse,
        #     cb_kwargs={'username': username,
        #                'user_id': user_id,
        #                'variables': deepcopy(variables)},
        # )

        # followers
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.user_followers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)},
        )

    # followers parse
    def user_followers_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            url_posts = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)},
            )
        followers = j_data.get('data').get('user').get('edge_followed_by').get('edges')
        for follower in followers:
            yield FollowerItem(
                name=follower['node']['username'],
                follower_id=follower['node']['id'],
                profile_photo_link=follower['node']['profile_pic_url'],
                username_who_is_subscribed_to=username,
                id_who_is_subscribed_to=user_id
            )

    # posts parse
    def user_posts_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            url_posts = f'{self.graphql_url}query_hash={self.post_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_posts_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)},
            )
        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
        for post in posts:
            item = InstaScraperItem(
                user_id=user_id,
                photo=post['node']['display_url'],
                likes=post['node']['edge_media_preview_like'],
                text=post['node']['edge_media_to_caption']['edges'][0]['node']['text']
            )

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')