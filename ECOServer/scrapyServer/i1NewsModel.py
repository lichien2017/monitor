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
from util.log import Logger
log = Logger()

class i1NewsParse(BaseParse):
    # 解析一点资讯
    def Analysis_ydzx(self, data, category, crawltime, y,categorytag):
        # try:
        #     date = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))#当前时间
        #     f = open("E:\\" + category + date + ".txt",'a')
        #     f.write(json.dumps(data))
        #     f.close()
        # except:
        #     print("文件未保存")
        try:
            cardSubType = data['cardSubType']
            if cardSubType == "special_topic":
                documents_list = data['documents']
                for d in documents_list:
                    self.add_ydzx_db(d, category, crawltime, y,categorytag)
        except:
            self.add_ydzx_db(data, category, crawltime, y,categorytag)

    # 一点资讯插入数据库
    def add_ydzx_db(self, data, category, crawltime, y,categorytag):
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 1  # 类型 1 图文 2 图片 3 视频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        tab = ""  # 标签
        gallary = ""
        IsArtID = False  # 是否为广告资讯
        content = ""  # 内容
        publish_timestr = ""
        publish_time = ""
        url = ""  # 跳转地址
        title = data['title']
        source = data['source']
        try:
            abstract = data['summary']
        except:
            log.debug("无summary")
        try:
            articleid = data['docid']
        except:
            log.debug("广告资讯")
            articleid = data['aid']
            if title == "":
                title = abstract
        try:
            image_list = data['image_urls']
            for i in image_list:
                if i != "":
                    logo += i + ","
        except:
            log.debug("无图片")
        try:
            card_label = data['card_label']['text']
            tab = card_label
        except:
            log.debug("无标签")
        try:
            url = data['url']
        except:
            log.debug("无url")
        try:
            publish_timestr = data['date']
            timeArray = time.strptime(publish_timestr, "%Y-%m-%d %H:%M:%S")
            publish_time = int(time.mktime(timeArray))
        except:
            log.debug("无时间")
        try:
            content_type = data['content_type']
            if content_type == "video":
                restype = 3
                content = data['video_url']
            elif content_type == "slides":
                restype = 2
                gallery_items = data['gallery_items']
                for g in gallery_items:
                    if g['img'] != "":
                        gallary += g['img'] + ","
                    if g['desc'] != "":
                        content += g['desc'] + "<br/>"
            elif content_type == "picture":
                logo = data['image']
        except:
            ctype = data['ctype']
            if ctype == "advertisement":
                IsArtID = True
                tab = data['tag']
                log.debug("广告")
        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        # 拼链接地址
        news_detail_url = 'https://a1.go2yd.com/Website/contents/content?docid=' + str(articleid)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        # 若不为广告资讯或者视频资讯，取资讯详细信息
        if IsArtID == False:
            if restype == 1:
                news_detail = requests.get(news_detail_url).json()['documents']
                if category == "美图":
                    news_title = news_detail[0]['title']
                    if news_title != "":
                        title = news_title
                        abstract = news_detail[0]['summary']
                content = news_detail[0]['content']
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

    def tryparse(self, str):
        # 转换编码格式
        strjson = str.decode("UTF-8", "ignore")
        # 转json对象
        strjson = json.loads(strjson)
        url = strjson['url']
        result = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(result.query, True)
        if url.find('news-list-for-best-channel') > -1:
            category = "推荐"
            categorytag = self.categroytag["%s" % category]
        elif url.find('news-list-for-hot-channel') > -1:
            category = "要闻"
            categorytag = self.categroytag["%s" % category]
        elif url.find('news-list-for-channel') > -1:
            channel_id = params['channel_id'][0]
            if channel_id == "21044074964":
                category = "美图"
                categorytag = self.categroytag["%s" % category]
            elif channel_id == "21044074724":
                category = "视频"
                categorytag = self.categroytag["%s" % category]
            elif channel_id == "21044074756":
                category = "图片"
                categorytag = self.categroytag["%s" % category]
            else:
                log.debug(url)
                return
        else:
            log.debug(url)
            return
        crawltime = strjson['time']
        # 获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['result']
        datalen = len(list)
        for y, x in enumerate(list):
            if category == "要闻" or category == "图片":
                if datalen == y + 1:
                    continue
            elif category == "视频" or category == "美图":
                if y == 0:
                    continue
            self.Analysis_ydzx(x, category, crawltime, y,categorytag)
