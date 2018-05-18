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
import requests as rq
# from bs4 import BeautifulSoup
from util.log import SingleLogger
#log = Logger()

class JiKeParse(BaseParse):
    # 解析即刻
    def Analysis_bdxw(self, data, category, crawltime, y, categorytag):

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


        if data['type']=='RECOMMENDED_MESSAGE':
            articleid = data['id']
            #属于资讯
            try:
                #视频资讯
                videofind = data['item']['video']
                video = 1
            except:
                video = 0
            if video == 1:
                #视频资讯
                restype = 3
                #封面图
                logo = data['item']['video']['image']['picUrl']
                # # 短地址
                # if data['item']['linkInfo']:
                #     url = data['item']['linkInfo']['originalLinkUrl']
                #     video = self.getVideo(url)
                #     if video and video != '':
                #         gallary += video +","
            elif len(data['item']['pictures']) > 0:
                #不为空就是图文信息
                restype = 2
                #循环取封面图
                for picUrl in data['item']['pictures']:
                    logo += picUrl['picUrl'] + ","
                    gallary += picUrl['picUrl'] + ","
            else:
                #纯文本
                restype = 1
            #标题
            title =data['item']['topic']['content']
            source =data['item']['topic']['content']
            #内容
            content =data['item']['content']
            #时间
            publish_timestr = data['item']['createdAt'][:-5].replace("T", " ");
            timeArray = time.strptime(publish_timestr, "%Y-%m-%d %H:%M:%S")
            publish_time = int(time.mktime(timeArray))  # string转成时间戳
            crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
            #短地址
            if data['item']['linkInfo']:
                url = data['item']['linkInfo']['originalLinkUrl']
            # 判断列表封面图末尾是否为，若是则进行删除
            if len(logo) > 0:
                logostr = logo[len(logo) - 1]
                if logostr == ",":
                    logo = logo[:-1]
            # 判断gallary末尾是否为，若是则进行删除
            if len(gallary) > 0:
                logostr = gallary[len(gallary) - 1]
                if logostr == ",":
                    gallary = gallary[:-1]
        else:
            return

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
        #暂时只抓取一个栏目，写死
        category = "推荐"
        categorytag = self.categroytag["%s" % category]
        crawltime = strjson['time']
        # 获取data
        data = strjson['data']
        try:
            data = json.loads(data)
            list = data['data']
            for y, x in enumerate(list):
                self.Analysis_bdxw(x, category, crawltime, y,categorytag)
        except:
            SingleLogger().log.debug("抓取数据不正常")
