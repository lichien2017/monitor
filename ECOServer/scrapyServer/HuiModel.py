# coding=utf-8
from scrapyServer.BaseModel import BaseParse
import urllib.parse
import json
import requests
from pymongo import MongoClient
import time
import datetime
import hashlib
import uuid
import sys
from util.log import SingleLogger
import requests as rq
from bs4 import BeautifulSoup
#log = Logger()

class HuiParse(BaseParse):
    # 解析惠头条
    def Analysis_bdxw(self, data, category, crawltime, y, categorytag):
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 1  # 类型 1 图文 2 图片 3 视频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        tab = ""  # 标签
        gallary = "" #详情图片，视频
        content = ""  # 内容

        #头条栏目暂时看到的都是图文新闻
        restype = 1
        content = self.getWen(data['url'])

        title = data['topic']
        url = data['url']
        source = data['source']
        #
        articleid = data['rowkey']

        publish_time = data['date']
        img_url = data['miniimg']
        for i in img_url:
            if i['src'] != "":
                logo += i['src'] + ","

        gallary = self.getImg(url)
        video = self.getVideo(url)
        if video and video != '':
            gallary = gallary + video

        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(publish_time) / 1000))
        SingleLogger().log.debug(title)
        # 判断列表封面图末尾是否为，若是则进行删除
        logolen = len(logo)
        if logolen > 0:
            logostr = logo[logolen - 1]
            if logostr == ",":
                logo = logo[:-1]
        sdata = {
            "title": title,
            "description": abstract,
            "content": content,
            "source": source,
            "pubtimestr": publish_timestr,
            "pubtime": publish_time,
            "crawltimestr": crawltimestr,
            "crawltime": crawltime,
            "status": 0,
            "shorturl": url,
            "logo": logo,
            "labels": tab,
            "keyword": "",
            "seq": seq,
            "identity": str(articleid),
            "appname": self.appname,
            "app_tag": self.apptag,
            "category_tag":categorytag,
            "category": category,
            "restype": restype,
            "gallary": gallary
        }
        self.db(sdata, articleid, title)

        # 获取图片main

    def getImgMain(self):
        html = rq.get(urls).text
        soup = BeautifulSoup(html, "html.parser")  # 文档对象
        imgStr = ""
        for k in soup.find_all('img'):  # 获取img
            imgStr += k['src'] + "、"
        return imgStr

        # 获取文字main

    def getWenMain(self):
        html = rq.get(urls).text
        soup = BeautifulSoup(html, "html.parser")  # 文档对象
        # imgStrArr = soup.find_all('div', class_="Nfgz6aIyFCi3vZUoFGKEr")
        imgStrArr = soup.find_all('body')
        print(len(imgStrArr))
        if len(imgStrArr) == 0:
            return ''
        else:
            return imgStrArr[0]

        # 获取视频main

    def getVideoMain(self):
        html = rq.get(urls).text
        soup = BeautifulSoup(html, "html.parser")  # 文档对象
        imgStr = ""
        for k in soup.find_all('video'):
            imgStr += k['src'] + "、"
        return imgStr

        # 获取图片

    def getImg(self, link):
        global urls
        urls = link
        return self.getImgMain()

        # 获取图文

    def getWen(self, link):
        global urls
        urls = link
        return str(self.getWenMain())

        # 获取视频

    def getVideo(self, link):
        global urls
        urls = link
        return self.getVideoMain()



    def tryparse(self, str):
        # 转换编码格式
        strjson = str.decode("UTF-8", "ignore")
        # 转json对象
        strjson = json.loads(strjson)
        url = strjson['post']
        if url.find('type=toutiao') > -1:
            category = "头条"
            categorytag = self.categroytag["%s" % category]
        elif url.find('type=yule') > -1:
            category = "娱乐"
            categorytag = self.categroytag["%s" % category]
        elif url.find('type=bagua') > -1:
            category = "八卦"
            categorytag = self.categroytag["%s" % category]
        elif url.find('type=shehui') > -1:
            category = "社会"
            categorytag = self.categroytag["%s" % category]
        elif url.find('type=guonei') > -1:
            category = "国内"
            categorytag = self.categroytag["%s" % category]
        elif url.find('type=guoji') > -1:
            category = "国际"
            categorytag = self.categroytag["%s" % category]
        crawltime = strjson['time']
        # 获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['data']['data']

        for y, x in enumerate(list):
            self.Analysis_bdxw(x, category, crawltime, y,categorytag)
