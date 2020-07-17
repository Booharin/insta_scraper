# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class FollowerItem(scrapy.Item):
    name = scrapy.Field()
    follower_id = scrapy.Field()
    profile_photo_link = scrapy.Field()
    username_who_is_subscribed_to = scrapy.Field()
    id_who_is_subscribed_to = scrapy.Field()
