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

class ZhiHuParse(BaseParse):
    # 解析知乎
    def Analysis_bdxw(self, data, category, crawltime, y, categorytag):
        # try:
        #    date = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))#当前时间
        #    f = open("E:\\" + category + date + ".txt",'a')
        #    f.write(json.dumps(data))
        #    f.close()
        # except :
        #    print("文件未保存")
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 1  # 类型 1 图文 2 图片 3 视频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        tab = ""  # 标签
        gallary = ""#文章中的图片
        content = ""  # 内容
        if category == "推荐":
            ctag = data['type']
            if ctag == "feed_advert":
                tab = "广告"
                return
            # 属于资讯
            try:
                # 视频资讯
                videofind = data['target']['thumbnail_extra_info']
                video = 1
            except:
                video = 0
            if video == 1:
                #文章中有视频
                restype = 3
                gallary = data['target']['thumbnail_extra_info']['playlist']['hd']['url']
            try:
                # 普通文章
                questionfind = data['target']['question']
                question = 1
            except:
                question = 0
            if question == 1:
                #普通文章
                title = data['target']['question']['title']
                logo = data['target']['thumbnail']
                # 短地址需要拼接
                # 取短地址拼接Id
                qId = str(data['target']['question']['id'])
                aId = str(data['target']['id'])
                url = "https://www.zhihu.com/question/"+qId+"/answer/"+aId+"?utm_source=qq&utm_medium=social"
            else:
                #公众号推文
                title = data['target']['title']
                logo = data['target']['image_url']
                Id = str(data['target']['id'])
                url = "https://zhuanlan.zhihu.com/p/"+Id+"?utm_source=qq&utm_medium=social"
            articleid = uuid.uuid1();
            #摘要
            abstract = data['target']['excerpt']
            #作者
            source = data['target']['author']['name']
            publish_time = data['target']['created_time']
            publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(publish_time) / 1000))

            content = ""
        elif category == "热榜":
            hottype =  data['target']['label_area']['type']
            if hottype == 'text':
                tab = data['target']['label_area']['text']


            title = data['target']['title_area']['text']
            articleid = data['id']
            logo = data['target']['image_area']['url']
            url = data['target']['link']['url']
            abstract = data['target']['excerpt_area']['text']
            # 没有发布时间，用当前时间暂替
            publish_time = crawltime
            publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
            content = ""

        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))

        SingleLogger().log.debug(title)
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
        if url.find('https://api.zhihu.com/topstory/recommend') > -1:
            category = "推荐"
            categorytag = self.categroytag["%s" % category]
        elif url.find('https://api.zhihu.com/topstory/hot-list?limit=1') > -1:
            category = "热榜"
            categorytag = self.categroytag["%s" % category]
        else:
            SingleLogger().log.debug(url)
            return
        crawltime = strjson['time']
        # 获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['data']
        for y, x in enumerate(list):
            self.Analysis_bdxw(x, category, crawltime, y,categorytag)

