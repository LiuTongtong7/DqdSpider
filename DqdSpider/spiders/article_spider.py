#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 
# Created by liutongtong on 2018/7/16 23:57
#

import datetime
import os
import pymysql
import scrapy
import scrapy.signals

from DqdSpider.items import ArticleItem
from DqdSpider.settings import MYSQL_CONFIG


class ArticleSpider(scrapy.Spider):
    name = 'article_spider'
    allowed_domains = ['dongqiudi.com']

    date_string = datetime.date.today().strftime("%Y-%m-%d")
    custom_settings = {
        'ITEM_PIPELINES': {
            'DqdSpider.pipelines.ArticleWriterPipeline': 300,
        },
        'LOG_FILE': './logs/{}-article.log'.format(date_string),
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ArticleSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def spider_opened(self, spider):
        self.conn = pymysql.connect(**MYSQL_CONFIG)

    def spider_closed(self, spider):
        self.conn.close()

    def start_requests(self):
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
        select_sql = "SELECT id, web_url FROM dongqiudi_articles WHERE save_html = FALSE AND display_time > '{}'".format(yesterday)
        with self.conn.cursor() as cur:
            cur.execute(select_sql)
            for row in cur.fetchall():
                yield scrapy.Request(url=row[1], callback=self.parse, meta={'id': row[0]})

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
        date_string = response.css('div.detail span.time::text').extract_first().split()[0]

        if not os.path.exists('./htmls/{}'.format(date_string)):
            os.mkdir('./htmls/{}'.format(date_string))
        with open('./htmls/{}/{}.html'.format(date_string, response.meta['id']), 'w') as fp:
            fp.write(response.body_as_unicode())

        update_sql = 'UPDATE dongqiudi_articles SET save_html = TRUE WHERE id = %(id)s'
        with self.conn.cursor() as cur:
            cur.execute(update_sql, {'id': response.meta['id']})
        self.conn.commit()
