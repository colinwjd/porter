#!/usr/local/bin/python3
# -*- coding:utf-8 -*-

import http
import logging
import os
import random
import re
import sys
import time
import urllib
from multiprocessing import Pool

from spider import SpiderHTML

__author__ = 'Colin Wang'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 收藏夹的地址
url = 'https://www.zhihu.com/collection/30822111'

# 本地存放的路径,不存在会自动创建
store_path = '/Users/junxi/Downloads/Awesome/zhihu'


class zhihuCollectionSpider(SpiderHTML):

    def __init__(self, pageStart, pageEnd, url):
        self._url = url
        self._pageStart = int(pageStart)
        self._pageEnd = int(pageEnd) + 1
        # 低于此赞同数的答案不收录
        self.downLimit = 0

    def start(self):
        # 遍历收藏夹的页数
        for page in range(self._pageStart, self._pageEnd):
            url = self._url + '?page=' + str(page)
            content = self.getUrl(url)
            questionList = content.find_all('div', class_='zm-item')
            # 遍历收藏夹的每个问题
            for question in questionList:
                Qtitle = question.find('h2', class_='zm-item-title')
                # 被和谐了
                if Qtitle is None:
                    logger.info('问题已不存在!')
                    continue

                questionStr = Qtitle.a.string
                Qurl = 'https://www.zhihu.com' + Qtitle.a['href']
                # 将问题中的特殊符号替换为#，以便作为文件名使用
                Qtitle = re.sub(r'[\\/:*?"<>]', '#', questionStr)
                logger.info('正在获取问题：' + Qtitle)
                try:
                    Qcontent = self.getUrl(Qurl)
                except Exception as e:
                    logger.warn('!!!获取问题失败!!!', e)

                answerList = Qcontent.find_all(
                    'div', class_='zm-item-answer  zm-item-expanded')
                # 处理答案列表
                self._processAnswer(answerList, Qtitle)
                # 慢点访问，防止ip被封
                time.sleep(5)

    def _processAnswer(self, answerList, Qtitle):
        j = 0
        for answer in answerList:
            j = j + 1
            # 获取赞同数
            upvoted = int(answer.find('span', class_='count').string.replace(
                'K', '000'))
            if upvoted < self.downLimit:
                logger.info('赞同数小于设定值，跳过该回答！')
                continue
            authorInfo = answer.find(
                'div', class_='zm-item-answer-author-info')
            author = {'introduction': '', 'link': ''}
            try:
                author['name'] = authorInfo.find(
                    'a', class_='author-link').string
                author['introduction'] = str(authorInfo.find(
                    'span', class_='bio')['title'])
                author['link'] = authorInfo.find(
                    'a', class_='author-link')['href']
            except AttributeError:
                author['name'] = '匿名用户' + str(j)
            except TypeError as e:
                logger.warn(e)

            file_name = os.path.join(store_path, Qtitle, 'info', author[
                                     'name'] + '_info.txt')
            # 已经抓取过
            if os.path.exists(file_name):
                continue

            self.saveText(file_name, '{introduction}\r\n{link}'.format(
                **author))
            logger.info('正在获取用户`{name}`的回答'.format(**author))
            answerContent = answer.find(
                'div', class_='zm-editable-content clearfix')
            # 被举报的用户没有答案内容
            if answerContent is None:
                continue

            imgs = answerContent.find_all('img')
            # 收录图片
            if len(imgs) != 0:
                self._getImgFromAnswer(imgs, Qtitle, **author)
            # 收录文字
            text = answerContent.div.string
            if len(text) != 0:
                self._getTextFromAnswer(text, Qtitle, **author)

    def _getImgFromAnswer(self, imgs, Qtitle, **author):
        i = 0
        for img in imgs:
            # 不抓取知乎的小图
            if 'inline-image' in img['class']:
                continue
            i = i + 1
            imgUrl = img['src']
            extension = os.path.splitext(imgUrl)[1]
            path_name = os.path.join(store_path, Qtitle, author[
                                     'name'] + '_' + str(i) + extension)
            try:
                self.saveImg(imgUrl, path_name)
            except Exception as e:
                logger.warn(e)

    # 收录文字
    def _getTextFromAnswer(self, content, Qtitle, **author):
        path_name = os.path.join(
            store_path, Qtitle, 'answer_text', author['name'] + '.txt')
        try:
            self.saveText(path_name, content)
        except Exception as e:
            logger.warn(e)

# 运行示例：zhihu.py 1 5   获取收藏夹1到5页的数据
if __name__ == '__main__':
    page, limit, paramsNum = 1, 0, len(sys.argv)
    if paramsNum >= 3:
        page, pageEnd = sys.argv[1], sys.argv[2]
    elif paramsNum == 2:
        page = sys.argv[1]
        pageEnd = page
    else:
        page, pageEnd = 1, 1

    spider = zhihuCollectionSpider(page, pageEnd, url)
    spider.start()
