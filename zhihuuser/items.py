# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
from scrapy import Item, Field


class UserItem(Item):
    id = Field()
    name = Field()
    type = Field()
    headline = Field()
    avatar_url = Field()
    answer_count = Field()
    articles_count = Field()
    avatar_url_template = Field()
    badge = Field()
    employments = Field()
    follower_count = Field()
    gender = Field()
    url = Field()
    url_token = Field()
    user_type = Field()
    is_advertiser = Field()
    is_blocking = Field()
    is_followed = Field()
    is_following = Field()
    is_org = Field()
    allow_message = Field()
