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
#log = Logger()

class DouYinParse(BaseParse):
    # 解析抖音
    def Analysis_bdxw(self, data, category, crawltime, y, categorytag):
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 3  # 类型 1 图文 2 图片 3 视频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        tab = ""  # 标签
        gallary = ""#文章中的图片
        content = ""  # 内容

        articleid = data['aweme_id'];
        #摘要
        abstract = data['desc']
        #标题
        title = data['desc']
        #作者
        source = data['author']['nickname']
        publish_time = data['create_time']
        publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(publish_time)))

        content = data['video']['play_addr']['url_list'][0]
        logo = data['video']['origin_cover']['url_list'][0]

        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))

        url = data['share_url']

        #详情中的视频
        video = data['video']['play_addr']['url_list'][0]

        # 详情中的音频
        audio = ''

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
            "gallary": gallary,
            "video": video,
            "audio": audio
        }
        self.db(sdata, articleid, title)

    def tryparse(self, str):
        # 转换编码格式
        strjson = str.decode("UTF-8", "ignore")
        # 转json对象
        strjson = json.loads(strjson)
        url = strjson['url']
        if url.find('/aweme/v1/feed/') > -1:
            category = "推荐"
            categorytag = self.categroytag["%s" % category]
        elif url.find('/aweme/v1/nearby/feed/') > -1:
            category = "附近"
            categorytag = self.categroytag["%s" % category]
        else:
            SingleLogger().log.debug(url)
            return
        crawltime = strjson['time']
        # 获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['aweme_list']
        for y, x in enumerate(list):
            self.Analysis_bdxw(x, category, crawltime, y,categorytag)

