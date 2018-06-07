# coding=utf-8
from scrapyServer.BaseModel import BaseParse
import urllib.parse
import json
from pymongo import MongoClient
import time
import datetime
import hashlib
import uuid
import sys
import requests as rq
from util.log import SingleLogger


class KuaishouParse(BaseParse):

    def Analysis_ks(self,data,category,crawltime,y,categorytag):
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 3 # 类型 1 图文 2 图片 3 视频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        tab = ""  # 标签
        gallary = ""
        content = ""  # 内容
        publish_timestr = ""
        publish_time = ""
        url = ""  # 跳转地址
        title=data['caption']
        source=data['user_name']
        # 封面图
        try:
            logo=data['cover_thumbnail_urls'][0]['url']
        except:
            logo = data['cover_thumbnail_urls'][1]['url']
        # 视频地址
        try:
            content=data['main_mv_urls'][0]['url']
        except:
            content = data['main_mv_urls'][1]['url']
        video = content
        publish_timestr = data['time']
        timeArray = time.strptime(publish_timestr, "%Y-%m-%d %H:%M:%S")
        publish_time = int(time.mktime(timeArray))
        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        # 详情中的音频
        audio = ''
        userId=''
        photoId=''
        share_info=data['share_info']
        params = share_info.split('&')
        for p in params:
            if p.find('userId') > -1:
                userId = p.split('=')[1]
            if p.find('photoId') > -1:
                photoId = p.split('=')[1]
                articleid=photoId

        if userId!='' and photoId!='':
            url = 'https://live.kuaishou.com/u/' + userId + '/' + photoId
        if photoId=='':
            articleid=data['photo_id']

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
            "category_tag": categorytag,
            "category": category,
            "restype": restype,
            "gallary": gallary,
            "video": video,
            "audio": audio
        }
        self.db(sdata, articleid, title)

    def tryparse(self,str):
             #转换编码格式
        strjson = str.decode("UTF-8","ignore")
        #转json对象
        strjson = json.loads(strjson)
        url = strjson['url']
        if url.find('rest/n/feed/hot') > -1:
            category = "发现"
            categorytag = self.categroytag["%s" % category]
        else:
            SingleLogger().log.debug(url)
            return ;
        crawltime = strjson['time']
        #获取data
        data = strjson['data']
        try:
            data = json.loads(data)
        except:
            None
        list=data['feeds']
        for y, x in enumerate(list):
            self.Analysis_ks(x, category, crawltime, y,categorytag)