#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created by liutongtong on 2018/7/15 10:39
#

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    user_id = scrapy.Field()
    type = scrapy.Field()
    display_time = scrapy.Field()
    thumb = scrapy.Field()
    comments_total = scrapy.Field()
    web_url = scrapy.Field()
    official_account = scrapy.Field()
