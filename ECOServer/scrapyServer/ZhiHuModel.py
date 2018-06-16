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
from util import *

from bs4 import BeautifulSoup
#log = Logger()

class ZhiHuParse(BaseParse):
    # 解析知乎
    def Analysis_bdxw(self, data, category, crawltime, y, categorytag):
        video = ''  # 视频
        audio = ''  # 音频
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
                videos = 1
            except:
                videos = 0
            if videos == 1:
                #文章中有视频
                restype = 3
                video = data['target']['thumbnail_extra_info']['playlist']['hd']['url']
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
                url = "https://zhuanlan.zhihu.com/p/"+Id
            articleid = uuid.uuid1();
            #摘要
            abstract = data['target']['excerpt']
            #作者
            source = data['target']['author']['name']
            publish_time = data['target']['created_time']
            publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(publish_time) / 1000))

            content = self.getHtmlBody(url)
            gallary = self.getHtmlImages(url)
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
            content = self.getHtmlBody(url)
            gallary = self.getHtmlImages(url)
        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))

        SingleLogger().log.debug(title)
        try:
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
        except Exception as ex :
            SingleLogger().log.error(ex)
            pass
        else:
            SingleLogger().log.debug(sdata)
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


   # 获取图片main

    # def getImgMain(self,url):
    #     # html = rq.get(urls).text
    #     html = Http.get(url)
    #     soup = BeautifulSoup(html, "html.parser")  # 文档对象
    #     imgStr = ""
    #     for k in soup.find_all('img'):  # 获取img
    #         imgStr += k['src'] + ","
    #     return imgStr
    #
    #     # 获取文字main
    #
    # def getWenMain(self,url):
    #     # html = rq.get(urls).text
    #     html = Http.get(url)
    #     soup = BeautifulSoup(html, "html.parser")  # 文档对象
    #     # imgStrArr = soup.find_all('div', class_="Nfgz6aIyFCi3vZUoFGKEr")
    #     imgStrArr = soup.find_all('body')
    #     print(len(imgStrArr))
    #     if len(imgStrArr) == 0:
    #         return ''
    #     else:
    #         return imgStrArr[0]
    #
    #     # 获取视频main
    #
    # def getVideoMain(self,url):
    #     # html = rq.get(urls).text
    #     html = Http.get(url)
    #     soup = BeautifulSoup(html, "html.parser")  # 文档对象
    #     imgStr = ""
    #     for k in soup.find_all('video'):
    #         imgStr += k['src'] + ","
    #     return imgStr
    #
    #     # 获取图片
    #
    # def getImg(self, link):
    #     # global urls
    #     # urls = link
    #     return self.getImgMain(link)
    #
    #     # 获取图文
    #
    # def getWen(self, link):
    #     # global urls
    #     # urls = link
    #     return str(self.getWenMain(link))
    #
    #     # 获取视频
    #
    # def getVideo(self, link):
    #     # global urls
    #     # urls = link
    #     return self.getVideoMain(link)


