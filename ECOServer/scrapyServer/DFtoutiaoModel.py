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

class dftoutiaoParse(BaseParse):
    def Analysis_dftt(self, data, category, crawltime, y, categorytag):
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 1  # 类型 1 图文 2 图片 3 视频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        tab = ""  # 标签
        gallary = ""
        content = ""  # 内容
        video = ''  # 视频
        audio = '' #音频
        articleid=data['rowkey']
        title=data['topic']
        try:
            hotnews=data['hotnews']
            if hotnews=="1":
                tab='热门'
        except:
            SingleLogger().log.debug('非热门')
        try:
            issptopic=data['issptopic']
            if issptopic=="1":
                if tab=='':
                    tab='专题'
                else:
                    tab+=',专题'
        except:
            SingleLogger().log.debug('非专题')
        try:
            imglist=data['miniimg']
            for i in imglist:
                if i['src'] != "":
                    logo += i['src'] + ","
        except:
            SingleLogger().log.debug('无封面图')
        try:
            url=data['shareurl']
        except:
            url = data['url']
        source=data['source']
        # 判断列表封面图末尾是否为，若是则进行删除
        logolen = len(logo)
        if logolen > 0:
            logostr = logo[logolen - 1]
            if logostr == ",":
                logo = logo[:-1]
        publish_time=data['ctrtime']
        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(publish_time) / 1000))
        # 滚动视频
        additional02=""
        try:
            additional02 = data['additional02']
        except:
            SingleLogger().log.debug('非滚动视频')
        if len(additional02)>0:
            for i in additional02:
                imglist = i['imgjs']
            for i in imglist:
                if i['src'] != "":
                    logo += i['src'] + ","
            source = i['source']
            videos = i['videojs']
            for v in videos:
                if v['src'] != "":
                    video += v['src'] + ","
                    content += v['src'] + ","
            articleid = i['8413148441964056151']
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
        else :
            isvideo = data['videonews']
            if isvideo == "1":
                restype = 3
                content = data['video_link']
                video = data['video_link']
            #普通资讯
            if restype == 1:
                if tab.find('专题')>-1:
                    content=url
                else:
                    dataurl=url+""
                    try:
                        gallary = self.getHtmlImages(url)
                    except:
                        SingleLogger().log.debug("没有gallary")
                    try:
                        content = self.getHtmlBodyInnerText(url)
                    except:
                        SingleLogger().log.debug("没有图文详情")
                    try:
                        videos = self.getHtmlVideos(url)
                        if videos != '':
                            video += videos
                    except:
                        SingleLogger().log.debug("详情没有video")
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
        post = strjson['post']
        crawltime = strjson['time']
        type=""
        if url.find('newsgzip') > -1:
            params = post.split('&')
            for p in params:
                if p.find('type') > -1:
                    type = p.split('=')[1]
                    break
            if type=='toutiao':
                category = "推荐"
                categorytag = self.categroytag["%s" % category]
            elif type=='redian':
                category = "热点"
                categorytag = self.categroytag["%s" % category]
        elif url.find('getvideosgzip') > -1:
            category = "视频"
            categorytag = self.categroytag["%s" % category]
        # 获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['data']
        for y, x in enumerate(list):
            self.Analysis_dftt(x, category, crawltime, y,categorytag)