#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 
# Created by liutongtong on 2018/7/15 10:03
#

import random

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from DqdSpider.middlewares import USER_AGENT_LIST


class RandomUserAgentMiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        ua = random.choice(USER_AGENT_LIST)
        request.headers.setdefault('User-Agent', ua)
