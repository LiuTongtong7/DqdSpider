#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created by liutongtong on 2018/7/15 10:39
#

import datetime
import json
import re
import scrapy

from DqdSpider.items import ArticleItem


class ListSpider(scrapy.Spider):
    name = 'list_spider'
    allowed_domains = ['dongqiudi.com']

    date_string = datetime.date.today().strftime("%Y-%m-%d")
    custom_settings = {
        'ITEM_PIPELINES': {
            'DqdSpider.pipelines.ArticleWriterPipeline': 300,
        },
        'LOG_FILE': './logs/{}-list.log'.format(date_string),
    }

    start_urls = ['http://dongqiudi.com/archives/1?page=1']
    # def start_requests(self):
    #     for page in range(1, 50):
    #         yield scrapy.Request(url='http://dongqiudi.com/archives/1?page={}'.format(page), callback=self.parse)

    @staticmethod
    def wrap_article(**kwargs):
        article = ArticleItem()
        for k in kwargs:
            if isinstance(kwargs[k], str):
                kwargs[k] = kwargs[k].strip()
                if len(kwargs[k]) == 0:
                    kwargs[k] = None
            article[k] = kwargs[k]
        return article

    def parse(self, response):
        self.logger.info('Parsing %s', response.url)
        data = json.loads(response.body_as_unicode())['data']
        for article in data:
            yield self.wrap_article(**article)

        article_times = map(lambda a: datetime.datetime.strptime(a['display_time'], "%Y-%m-%d %H:%M:%S"), data)
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
        yesterday = datetime.datetime.strptime(yesterday, "%Y-%m-%d %H:%M:%S")

        url = response.url.split('?')[0]
        m = re.match('.*page=(\d+).*', response.url)
        if not m:
            self.logger.error('URL %s doesnt have page', response.url)
            return

        next_page = int(m.group(1)) + 1
        if max(article_times) >= yesterday and next_page < 50:
            yield scrapy.Request(url='{}?page={}'.format(url, next_page), callback=self.parse)
