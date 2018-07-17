#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 
# Created by liutongtong on 2018/7/15 10:02
#

import json
import logging
import random


def set_logging_from_scrapy(settings):
    level_names = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
        'SILENT': logging.CRITICAL + 1
    }
    if settings.getbool('LOG_ENABLED'):
        log_level = level_names[settings.get('LOG_LEVEL')]
        if not settings.get('LOG_FILE'):
            scrapy_handler = logging.StreamHandler()
        else:
            scrapy_handler = logging.FileHandler(settings.get('LOG_FILE'),
                                                 encoding=settings.get('LOG_ENCODING'))
        # scrapy_handler.setLevel(log_level)
        scrapy_formatter = logging.Formatter(settings.get('LOG_FORMAT'))
        scrapy_handler.setFormatter(scrapy_formatter)
        logging.basicConfig(handlers=[scrapy_handler], level=log_level)


def set_logging_for_debug():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logging.basicConfig(handlers=[handler], level=logging.DEBUG)


USER_AGENT_LIST = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0'
]
