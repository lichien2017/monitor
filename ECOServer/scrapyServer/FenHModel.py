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
class FenHParse(BaseParse):

    #post请求
    def httpPost(self,url, postdata ):
        detailJson = requests.post(url, data=postdata).json()
        return detailJson

    #解析凤凰新闻
    def Analysis_fenghuang(self,data,category,crawltime,y):
        title = "" #标题
        abstract = "" #摘要
        articleid = "" #文章标识
        tab = "" #标签
        source = "" #来源
        logo = "" #列表图片
        url = "" #文章短地址
        articletype = "" #文章展示类型（phvideo-视频 doc-图文）
        publish_time = "" #发布时间 时间戳
        publish_timestr = "" #发布时间 标准时间str
        crawltimestr = "" #抓包时间
        restype = 1 #类型 1 图文 2 图片 3 视频
        seq = y + 1 #排序
        keywords = "" #关键字
        content = "" #内容
        gallary = "" #图片资讯图片地址
        detailJk = "" #详情接口

        #如果是推荐关注列表，直接return
        try:
            articletype = data['type']#文章展示类型
            if articletype == 'marquee2':
                return
        except:
            log.debug("无articletype")
            return

        # 标题
        try:
            title = data['title']
        except:
            log.debug('无标题')

        # 发布时间
        try:
            publish_timestr = data['updateTime']  #发布时间 标准时间str
            timeArray = time.strptime(publish_timestr, "%Y/%m/%d %H:%M:%S")
            publish_time = int(time.mktime(timeArray)) #string转成时间戳
        except:
            log.debug("无发布时间")

        # 抓包时间
        try:
            crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))  # 抓包时间
        except:
            log.debug("获取抓包时间失败")

        # 来源
        try:
            source = data['source']
        except:
            log.debug("没有来源或者是视频、广告")

        #没有link字段就return
        try:
            linkInfo = data['link']
        except:
            return

        # 短地址
        try:
            url = linkInfo['weburl']
        except:
            log.debug("无短地址")

        # 文章标识
        try:
            articleid = data['documentId']
        except:
            log.debug("没有文章标识或者是广告")

        #列表图logo
        #style.images里面没有就取thumbnail
        try:
            images = data['style']['images']
            if images and len(images) > 0:
                for imgobj in images:
                    logo += imgobj+"、"
            else:
                logo = data['thumbnail']
                if logo == "":
                    log.debug('无列表图')
        except:
            try:
                logo = data['thumbnail']
            except:
                log.debug('无列表图')

        #分类处理
        # 视频,或 小视频栏目
        if articletype == 'phvideo' or articletype == "videoshortimg":
            restype = 3
            try:
                source = data['phvideo']['channelName'] #来源
            except:
                log.debug("视频无来源")
            # 防止报错
            try:
                guid = data['id'] #视频接口参数
                articleid = guid  # 文章标识
                #没有MP4字段就调用详情接口
                try:
                    content = linkInfo['mp4']
                except:
                    detailJk = "http://api.3g.ifeng.com/api_phoenixtv_details?guid=" + guid #视频详情接口
                    postData = {}
                    res =self.httpPost(detailJk, postData)
                    content = res['singleVideoInfo'][0]['videoURLMid']
            except:
                log.debug("获取视频详情失败")

        #图片栏目、图片新闻
        elif articletype == "photo" or articletype == "slide":
            restype = 2
            #防止报错
            try:
                detailJk = linkInfo['url']  # 详情接口地址
                postData = {}
                res = self.httpPost(detailJk, postData)
                #图片类型的如果有slide字段就取，没有就按照普通新闻的接口来
                try:
                    slides = res['body']['slides']
                    if len(slides) > 0:
                        for sldobj in slides:
                            curDesc = sldobj['description']
                            curImg = sldobj['image']
                            if curDesc != "":
                                content += curDesc+"<br/>"
                            if curImg != "":
                                gallary += curImg+"、"
                except:
                    try:
                        content = res['body']['text']
                    except:
                        log.debug("无text")
                    try:
                        gallaryList = res['body']['img']
                        if len(gallaryList) > 0:
                            for gaobj in gallaryList:
                                gallary += gaobj['url'] + "、"
                    except:
                        log.debug("详情没有图片")
                    try:
                        videos = res['body']['videos']
                        for vidobj in videos:
                            gallary += vidobj['video']['Normal']['src'] + "、"
                    except:
                        log.debug("详情没有视频")
            except:
                log.debug("获取图片详情失败")

        #广告
        elif articletype == "advert":
            if tab == "":
                tab = "广告"
            else:
                tab += "、广告"
            try:
                articleid = data['pid'] #文章标识
            except:
                log.debug("该广告没有文章标识")

        #普通新闻
        elif articletype == "doc":
            #防止报错
            try:
                detailJk = linkInfo['url']  #详情接口地址
                postData = {}
                res = self.httpPost(detailJk, postData)
                try:
                    content = res['body']['text']
                except:
                    log.debug("无text")
                try:
                    gallaryList = res['body']['img']
                    if len(gallaryList) > 0:
                        for gaobj in gallaryList:
                            gallary += gaobj['url']+"、"
                except:
                    log.debug("详情没有图片")
                try:
                    videos = res['body']['videos']
                    for vidobj in videos:
                        gallary += vidobj['video']['Normal']['src']+"、"
                except:
                    log.debug("详情没有视频")
            except:
                log.debug("获取图文详情失败")

        # 置顶新闻
        elif articletype == "topic2":
            if tab == "":
                tab = "置顶"
            else:
                tab += "、置顶"

        sdata = {
            "title": title,
            "description": abstract,
            "content": content,#
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
            "identity": str(articleid),
            "appname": "凤凰新闻",
            "category": category,#栏目
            "restype": restype,#
            "gallary": gallary#里面的所有图片地址
        }
        self.db(sdata, articleid, title)

    def tryparse(self,str):
         #转换编码格式
        strjson = str.decode("UTF-8","ignore")
        #转json对象
        strjson = json.loads(strjson)
        url = strjson['url']
        result = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(result.query,True)
        category = ""#类型
        #区分栏目
        if url.find('api.3g.ifeng.com/get_pic_list?channel=news') > -1:
            category = "图片"
        elif url.find('api.iclient.ifeng.com/ClientNews') > -1:
            category = params['id'][0]
            if category == "SYLB10,SYDT10,SYRECOMMEND" or category == "SYLB10,SYDT10":
                category = "头条"
            elif category == "RECOMVIDEO":
                category = "视频"
            elif category == "YAOWEN223":
                category = "要闻"
            elif category == "VIDEOSHORT":
                category = "小视频"
            else:
                log.debug("有不正确的url1")
                return
        else:
            log.debug("有不正确的url2")
            return
        crawltime = strjson['time']
        #获取data
        data = strjson['data']
        data = json.loads(data)

        #如果是“图片”栏目,取item方式不一样
        if category == "图片":
            item = data['body']['item']
            for y, x in enumerate(item):
                self.Analysis_fenghuang(x, category, crawltime, y)
        else:
            for y1, curobj1 in enumerate(data):
                item = curobj1['item']
                for y2, curobj2 in enumerate(item):
                    self.Analysis_fenghuang(curobj2, category, crawltime, y2)