#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created by liutongtong on 2018/7/15 10:39
#

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import pymysql

from DqdSpider.items import ArticleItem
from DqdSpider.settings import MYSQL_CONFIG


class ArticleWriterPipeline(object):
    def open_spider(self, spider):
        self.conn = pymysql.connect(**MYSQL_CONFIG)

    def close_spider(self, spider):
        self.conn.close()

    insert_sql = 'INSERT INTO dongqiudi_articles (id, title, description, user_id, type, ' \
                 'display_time, thumb, comments_total, web_url, official_account) ' \
                 'VALUES (%(id)s, %(title)s, %(description)s, %(user_id)s, %(type)s, ' \
                 '%(display_time)s, %(thumb)s, %(comments_total)s, %(web_url)s, %(official_account)s)'
    update_sql = 'UPDATE dongqiudi_articles ' \
                 'SET title=%(title)s, description=%(description)s, user_id=%(user_id)s, type=%(type)s, ' \
                 'display_time=%(display_time)s, thumb=%(thumb)s, comments_total=%(comments_total)s, ' \
                 'web_url=%(web_url)s, official_account=%(official_account)s, save_time=%(save_time)s ' \
                 'WHERE id=%(id)s'

    def process_item(self, item, spider):
        if isinstance(item, ArticleItem):
            self.process_article(item)
        else:
            return item

    def process_article(self, item):
        try:
            with self.conn.cursor() as cur:
                cur.execute(self.insert_sql, dict(item))
            self.conn.commit()
        except pymysql.err.IntegrityError:
            with self.conn.cursor() as cur:
                cur.execute(self.update_sql, dict(dict(item), save_time=datetime.datetime.now()))
            self.conn.commit()
        return "Article {} is inserted".format(item['id'])
