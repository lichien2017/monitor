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

class TencentParse(BaseParse):

   #解析腾讯新闻
    def Analysis_ten(self,data,category,crawltime,y,categorytag):
        video = ''  # 视频
        audio = ''  # 音频
        #标题
        title = ""
        try:
            title = data['title']#标题
        except:
            SingleLogger().log.debug('无标题')
        #摘要
        abstract = ""
        try:
            abstract = data['abstract']#摘要
        except:
            SingleLogger().log.debug("无摘要")
        #文章标识
        articleid = ""
        try:
            articleid = data['id']#文章标识
            #如果文章标识为空，则跳出此循环
            if articleid == "":
                return
        except:
            SingleLogger().log.debug("无文章标识")
        menulable=""
        #当前栏目标签
        try:
            menulable=data['uinname']
        except:
            SingleLogger().log.debug("无栏目标签")
        #图片
        logo = ""
        #来源
        source = ""
        #资讯地址
        url = ""
        try:
            source = data['source']
        except :
            SingleLogger().log.debug("无来源")
        try :
            url = data['url']#分享地址
            if not(url) or url=="":
                url = data['short_url']  # 分享地址
                if not (url) or url == "":
                    url = data['surl']  # 分享地址
        except:
            SingleLogger().log.debug("无资讯地址")
        #发布时间 时间戳
        publish_time = ""
        #发布时间 标准时间
        publish_timestr = ""
        try:
            publish_time = data['timestamp']
            if publish_time and publish_time != "":
                publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(publish_time))
        except:
            SingleLogger().log.debug("无发布时间")

        # 抓包时间
        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))  # 抓包时间
        #类型 1 图文 2 图片 3 视频
        restype = 1
        #排序
        seq = y + 1
        #关键字
        keywords = ""
        #标签
        tab = ""
        try:
            zdTab = data['labelList'][0]['word']
            if tab == "":
                tab = zdTab
            else:
                tab += ","+zdTab
        except:
            SingleLogger().log.debug("无标签")
        try:
            zdTab = data['up_labelList'][0]['word']
            if tab != '':
                tab += ',' + zdTab
            else:
                tab = zdTab
        except:
            SingleLogger().log.debug("无特殊标签")
        #文章展示类型（528-热点精选 88-问答）
        articletype = ""
        try:
            articletype = data['articletype']
        except:
            SingleLogger().log.debug("无articletype")
            return

        #内容
        content = ""

        #图片资讯图片地址
        gallary = ""

        #列表图片展示类型（1-没图 0-1张小图 3-1张大图 2-3张小图）
        picShowType = ""
        try :
            picShowType = data['picShowType']
        except :
            SingleLogger().log.debug("无picShowType")

        #logo 图片列表(除了视频板块)
        if picShowType == 1:#无图
            #列表没有图
            logo = ""
        else:
            #在thumbnails_qqnews数组里面取值
            try:
                image_list = data['thumbnails_qqnews']
                if not(image_list):
                    image_list = data['thumbnails_qqnews_photo']
                    if not (image_list):
                        image_list = data['thumbnails']
                logo = ""
                for i in image_list:
                    if i != "":
                        logo+=i + ","
            except:
                SingleLogger().log.debug("没有列表图,可能没有图或是视频")

        if articletype == "528" or articletype == "525": #528,525-热点精选
            if tab == "":
                tab = "热点精选"
            else:
                tab += ",热点精选"
            try:
                #热点新闻，取里面第一个列表的
                childList = data['newsModule']['newslist'][0]
                title = childList['title']
                source = childList['source']
                abstract = childList['abstract']  # 摘要
                logo = childList['thumbnails_qqnews'][0]
                if not(logo):
                    logo = childList['thumbnails_qqnews_photo'][0]
                    if not (logo):
                        logo = childList['thumbnails'][0]
                try:
                    url = data['url']  # 分享地址
                    if not (url) or url == "":
                        url = data['short_url']  # 分享地址
                        if not (url) or url == "":
                            url = data['surl']  # 分享地址
                except:
                    SingleLogger().log.debug("无资讯地址")
                content=url
            except:
                SingleLogger().log.debug("该条热点消息无内容")

        elif articletype == "4" or articletype == "101": #视频新闻 4,101
            restype = 3#视频
            try:
                videoData = data["video_channel"]["video"]
                logo = videoData["img"]
                content = videoData["playurl"]
                video=content
            except:
                SingleLogger().log.debug('无视频')

        elif articletype == "533": #直播
            restype = 3  # 视频
            if tab=="":
                tab="直播"
            else:
                tab+=",直播"
            liveVideo = data["newsModule"]["newslist"][0]
            title = liveVideo['title']
            source = liveVideo['source']
            abstract = liveVideo['abstract']
            logo = liveVideo['thumbnails_qqnews'][0]
            if not (logo):
                logo = liveVideo['thumbnails_qqnews_photo'][0]
                if not (logo):
                    logo = liveVideo['thumbnails'][0]
            try:
                publish_time = liveVideo['timestamp']# 发布时间 时间戳
                if publish_time and publish_time != "":
                    publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(publish_time))# 发布时间 标准时间
            except:
                SingleLogger().log.debug("无发布时间")
            try:
                url = liveVideo['url']  # 分享地址
                if not (url) or url == "":
                    url = liveVideo['short_url']  # 分享地址
                    if not (url) or url == "":
                        url = liveVideo['surl']  # 分享地址
                try:
                    video_channel=liveVideo['video_channel']['video']['playurl']
                    content=video_channel
                except:
                    content=url
                video=content
            except:
                SingleLogger().log.debug("无分享地址")

        elif articletype == "526": #标签列表，不是新闻return
            return
            # 普通新闻 图片新闻
        elif articletype == "0" or articletype == "12" or articletype=="1":
            news_detail_url = 'http://r.inews.qq.com/getSimpleNews/1.3.1_qqnews_5.5.90/' + str(menulable)+'/'+str(articleid)
            news_detail = rq.get(news_detail_url).json()
            if articletype == "0" or articletype == "12":
                content=news_detail['content']['text']
                attribute = news_detail['attribute']
                for a in attribute:
                    try:
                        # 判断gallary是否存在此链接地址，存在则跳出此次循环，不存在则进行拼接
                        if gallary.find(attribute[a]["url"]) > -1:
                            continue
                        else:
                            gallary += attribute[a]["url"] + ","
                    except:
                        try:
                            video += attribute[a]["playurl"] + ","
                        except:
                            try:
                                audio += attribute[a]["murl"] + ","
                            except:
                                SingleLogger().log.debug(json.dumps(attribute))
            elif articletype=="1":
                restype=2 #图片新闻
                attribute = news_detail['attribute']
                for a in attribute:
                    try:
                        # 判断gallary是否存在此链接地址，存在则跳出此次循环，不存在则进行拼接
                        if gallary.find(attribute[a]["url"]) > -1:
                            continue
                        else:
                            gallary += attribute[a]["url"] + ","
                            content+=attribute[a]['desc']+"<br/>"
                    except:
                         SingleLogger().log.debug(json.dumps(attribute))
            #专题新闻
        elif articletype=="100":
            content=url
        sdata = {
            "title": title,
            "description": abstract,
            "content": content,
            "source": source,
            "pubtimestr": publish_timestr,
            "pubtime": publish_time,
            "crawltimestr": crawltimestr,#抓包时间
            "crawltime": crawltime,
            "status": 0,
            "shorturl": url,
            "logo": logo,
            "labels": tab,
            "keyword": "",
            "seq": seq,
            "identity":str(articleid),
            "appname": self.appname,
            "app_tag": self.apptag,
            "category_tag":categorytag,
            "category": category,#栏目
            "restype": restype,#类型
            "gallary": gallary,
            "video": video,
            "audio": audio
        }
        self.db(sdata,articleid,title)


    def tryparse(self,str):
         #转换编码格式
        strjson = str.decode("UTF-8","ignore")
        #转json对象
        strjson = json.loads(strjson)
        url = strjson['url']
        result = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(result.query,True)
        category = ""#类型
        try:
            category = params['chlid'][0]
            if category == "news_news_top":
                category = "要闻"
                categorytag = self.categroytag["%s" % category]
            elif category == "news_news_lianghui":
                category = "两会"
                categorytag = self.categroytag["%s" % category]
            elif category == "news_video_top":
                category = "视频"
                categorytag = self.categroytag["%s" % category]
            elif category == "news_video_main":
                category = "图片"
                categorytag = self.categroytag["%s" % category]
            else:
                SingleLogger().log.debug("不在4种类型之内")
                return
        except :
            SingleLogger().log.debug("无类型")
            return
        crawltime = strjson['time']
        #获取data
        data = strjson['data']
        try:
            data = json.loads(data)
        except:
            None
        #防止报错
        try:
            #如果是“两会”,取newslist方式不一样
            if category == "两会":
                list = data['idlist'][0]['newslist']
            else:
                list = data['newslist']
        except:
            return
        for y, x in enumerate(list):
            self.Analysis_ten(x, category, crawltime, y,categorytag)