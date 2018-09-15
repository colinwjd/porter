#!/usr/local/bin/python3
# -*- coding:utf-8 -*-

__author__ = 'Colin Wang'

import os
import logging
from bs4 import BeautifulSoup
from spider import SpiderHTML


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

output = '~/Downloads/nuclear_oztf.txt'

help_url = 'http://1024.hlork9.pw/pw/thread.php?fid=17&page=1'
target_url = 'http://1024.hlork9.pw/pw/htm_data/17/1809/1285939.html'

class NuclearSpider(SpiderHTML):

    def __init__(self, pageStart, pageEnd, url):
        self._url = url
        self._pageStart = int(pageStart)
        self._pageEnd = int(pageEnd) + 1

    def start(self):
        for page in range(self._pageStart, self._pageEnd):
            url = self._url + str(page) + '.html'
            logger.info('url is %s' % url)
            soup = self.getUrl(url)
            title = soup.body.find('span', id='subject_tpc').get_text()
            content = soup.body.find('div', id='read_tpc').get_text()
            result = '标题：' + title + '\n' + '正文：' + content + '\n\n'
            self.saveText(output, result, mode='a')
            logger.info('part %s done.' % page)


if __name__ == '__main__':
    nuclear = NuclearSpider(1273782, 1285939, 'http://1024.hlork9.pw/pw/htm_data/17/1809/')
    nuclear.start()
