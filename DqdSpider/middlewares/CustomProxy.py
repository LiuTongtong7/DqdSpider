#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Created by liutongtong on 2018/6/27 03:02
#

import logging
import pymysql
import queue
import random
import threading
import time
import urllib.request

from DqdSpider.middlewares import set_logging_from_scrapy, set_logging_for_debug
from DqdSpider.middlewares import USER_AGENT_LIST


class AutoProxyMiddleware(object):
    logger = logging.getLogger(__name__ + '.AutoProxyMiddleware')

    config = {
        'enable': False,
        'delay': 600,
        'test_threads': 16,
        'test_cases': [
            ('http://dongqiudi.com/archives/1?page=10', '"tab_id":"1"', 'utf-8'),
        ],
        'test_timeout': 5,
        'ban_codes': [500, 502, 503, 504, 400, 403, 408],
        'concurrent_proxy': 8
    }

    def __init__(self, proxy_config=None):
        self.config.update(proxy_config or {})
        self.candidate_proxies = queue.Queue()
        self.verified_proxies = queue.Queue()

        self._fetch_proxies()
        self._verify_new_proxies(block=True)
        self.logger.info('Fetched about %d proxies', self.verified_proxies.qsize())

    @classmethod
    def from_crawler(cls, crawler):
        set_logging_from_scrapy(crawler.settings)
        return cls(dict(crawler.settings.getdict('PROXY_CONFIG'),
                        mysql_config=crawler.settings.getdict('MYSQL_CONFIG')))

    def process_request(self, request, spider):
        if not self._is_proxy_enabled(request):
            return  # continue processing this request

        if not self._has_enough_proxies():
            time.sleep(self.config['delay'])
            self._fetch_proxies()
            self._verify_new_proxies()
        while not self._has_enough_proxies():
            self.logger.debug('Waiting for new proxies...')
            time.sleep(1)
        self._set_proxy(request)

    def process_response(self, request, response, spider):
        if not self._is_proxy_enabled(request):
            return response  # continue processing this response

        proxy = self._get_proxy(request)
        if response.status not in self.config['ban_codes']:
            self._valid_proxy(proxy)
            return response
        else:
            self.logger.debug('Proxy %s is banned (http status %d) when crawling %s.',
                              proxy, response.status, request.url)
            self._invalid_proxy(proxy)
            request.dont_filter = True
            return request

    def process_exception(self, request, exception, spider):
        proxy = self._get_proxy(request)
        self.logger.debug('Proxy %s raised exception (%s) when crawling %s.', proxy, exception, request.url)
        self._invalid_proxy(proxy)
        request.dont_filter = True
        return request

    def _is_proxy_enabled(self, request):
        return self.config['enable'] and 'dont_proxy' not in request.meta

    def _has_enough_proxies(self):
        return not self.verified_proxies.empty()
        # return self.verified_proxies.qsize() >= self.config['min_limit']

    def _set_proxy(self, request):
        proxy, count = self.verified_proxies.get()
        if count < self.config['concurrent_proxy']:
            self.verified_proxies.put((proxy, count + 1))
        request.meta['proxy'] = proxy

    @staticmethod
    def _get_proxy(request):
        return request.meta['proxy']

    def _valid_proxy(self, proxy):
        self.verified_proxies.put((proxy, 1))

    def _invalid_proxy(self, proxy):
        pass

    def _fetch_proxies(self):
        self.logger.info('Start fetching new proxies...')
        conn = pymysql.connect(**self.config['mysql_config'])
        with conn.cursor() as cur:
            cur.execute('SELECT ip, port FROM proxies ORDER BY rand() LIMIT 100')
            for row in cur.fetchall():
                proxy = '{}://{}:{}'.format('http', row[0], row[1])
                self.candidate_proxies.put(proxy)
        conn.close()

    def _verify_new_proxies(self, block=False):
        self.logger.info('Start verifying new proxies...')
        threads = []
        for i in range(self.config['test_threads']):
            t = ProxyVerifier(self.candidate_proxies, self.verified_proxies,
                              self.config['test_cases'], self.config['test_timeout'], block)
            threads.append(t)
            t.start()
        if block:
            self.candidate_proxies.join()
            for i in range(self.config['test_threads']):
                self.candidate_proxies.put(None)


class ProxyVerifier(threading.Thread):
    logger = logging.getLogger(__name__ + '.ProxyVerifier')

    def __init__(self, candidate_proxies, verified_proxies, test_cases, timeout, block=False):
        super().__init__()
        self.candidate_proxies = candidate_proxies
        self.verified_proxies = verified_proxies
        self.test_cases = test_cases
        self.timeout = timeout
        self.block = block
        self.logger.info('Start a new ProxyVerifier thread...')

    def run(self):
        if self.block:
            while True:
                proxy = self.candidate_proxies.get()
                if proxy is None:
                    break
                if self.verify_proxy(proxy):
                    # self.logger.info('Proxy %s is verified.', proxy)
                    self.verified_proxies.put((proxy, 1))
                self.candidate_proxies.task_done()
        else:
            try:
                while True:
                    proxy = self.candidate_proxies.get_nowait()
                    if self.verify_proxy(proxy):
                        self.verified_proxies.put((proxy, 1))
                    self.candidate_proxies.task_done()
            except queue.Empty:
                pass

    def verify_proxy(self, proxy):
        proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-Agent', random.choice(USER_AGENT_LIST))]
        try:
            for url, code, charset in self.test_cases:
                html = opener.open(url, timeout=self.timeout).read().decode(charset)
                if code not in html:
                    return False
            return True
        except Exception:
            return False


def test_proxy(proxy):
    url = 'http://icanhazip.com/'
    proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
    opener = urllib.request.build_opener(proxy_handler)
    html = opener.open(url, timeout=5).read().decode('utf-8')
    print(html)


if __name__ == '__main__':
    set_logging_for_debug()
    apm = AutoProxyMiddleware()

    # proxy = 'http://xxx.xxx.xxx.xxx:xxxx'
    # test_proxy(proxy)
