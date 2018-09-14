#!/usr/local/bin/python3
# -*- coding:utf-8 -*-

__author__ = 'Colin Wang'

import os
import logging
from bs4 import BeautifulSoup
from spider import SpiderHTML


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

input_path = './books'
output = './book/nuclear.txt'


class NuclearSpider(SpiderHTML):

    def __init__(self, pageStart, pageEnd):
        self._pageStart = pageStart
        self._pageEnd = pageEnd

    def start(self):
        for page in range(self._pageStart, self._pageEnd + 1):
            filename = '12778p%s.html' % page
            logger.info('Loading file: %s' % filename)
            path = os.path.join(input_path, filename)
            soup = self.loadFromFile(path, coding='gbk')
            [script.extract() for script in soup('script')]
            title = soup.h1.string
            content = soup.body.find('div', class_='mcc').get_text()
            result = '标题：' + title + '\n' + '内容：' + content + '\n\n'
            self.saveText(output, result, mode='a')
            logger.info('part %s done.' % page)


if __name__ == '__main__':
    nuclear = NuclearSpider(1, 152)
    nuclear.start()
