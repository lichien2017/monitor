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

class SohuParse(BaseParse):

    #解析搜狐新闻
    def Analysis_shxw(self,data,category,crawltime,y):
        #try:
        #    date = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))#当前时间
        #    f = open("E:\\" + category + date + ".txt",'a')
        #    f.write(json.dumps(data))
        #    f.close()
        #except:
        #    print("文件未保存")
        seq = y + 1#排序
        title = ""#标题
        articleid = ""#文章标识
        restype = 1#类型 1 图文 2 图片 3 视频
        logo = ""#图片
        source = ""#来源
        abstract = ""#摘要
        tab = ""#标签
        gallary = ""
        IsArtID = False#是否为广告资讯
        content = ""#内容
        publish_timestr = ""
        publish_time = ""
        url = ""#跳转地址
        try:
            articleid = data['newsId']
        except:
            log.debug("广告")
        try:
            title = data['title']
        except:
            log.debug("无标题")
        try:
            source = data['media']
        except:
            log.debug("无来源")
        try:
            abstract = data['description']
        except:
            log.debug("无描述")
        try:
            tab = data['recomReasons']
        except:
            log.debug("无标签")
        try:
            img_list = data['pics']
            for i in img_list:
                if i != "":
                    logo+=i + ","
        except:
            log.debug("无图片")
        templateType=data['templateType']
        if templateType==14:
            IsArtID=True
            tab="广告"
            articleid=data['data']['adid']
            title=data['data']['resource']['text']
            logo=data['data']['resource1']['file']
            source=data['data']['resource2']['text']
        elif templateType==37:
            restype=3
        try:
            publish_time = data['time']
            publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(publish_time) / 1000))
        except:
            log.debug("无时间")
        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        news_detail_url = 'https://zcache.k.sohu.com/api/news/cdn/v5/article.go/' + str(articleid) + '/0/0/0/3/1/18/40/5/1/1/1522743246021.json'
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        if IsArtID==False:
            if restype == 3:
                vid = data['vid']
                if vid!=0:
                    news_detail_url = 'https://s1.api.tv.itc.cn/v4/video/info/' + str(vid) + '.json?site=2&api_key=695fe827ffeb7d74260a813025970bd5'
                    news_detail = requests.get(news_detail_url,headers=headers).json()
                    content = news_detail['data']['download_url']
                    url = news_detail['data']['url_html5']
            else:
                news_detail = requests.get(news_detail_url,headers=headers).json()
                content = news_detail['content']
                gallary_list = news_detail['photos']
                for g in gallary_list:
                    if g['pic'] != "":
                        gallary+=g['pic'] + ","
                tvInfos = news_detail['tvInfos']
                for t in tvInfos:
                    if t['tvUrl'] != "":
                        #如果不为视频地址，则通过视频ID调用接口，返回视频地址
                        if t['tvUrl']=="urlNor&prod=news&prod=h5,":
                            vid = t['vid']
                            news_detail_url = 'https://s1.api.tv.itc.cn/v4/video/info/' + str(vid) + '.json?site=2&api_key=695fe827ffeb7d74260a813025970bd5'
                            news_detail = requests.get(news_detail_url,headers=headers).json()
                            gallary+=  news_detail['data']['download_url']+ ","
                        else:
                            gallary+=t['tvUrl'] + ","
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
            "identity":str(articleid),
            "appname": "搜狐新闻",
            "category": category,
            "restype": restype,
            "gallary": gallary
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
        channelId = params['channelId'][0]
        if url.find('v6/news.go') > -1:
            if channelId == "1":
                category ="要闻"
            elif channelId == "13557":
                category = "推荐"
            else:
                log.debug(url)
                return
        elif url.find('v5/news.go') > -1:
            if channelId == "4313":
                category = "两会"
            else:
                log.debug(url)
                return
        else:
            log.debug(url)
            return
        crawltime = strjson['time']
        #获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['recommendArticles']
        for y,x in enumerate(list):
            self.Analysis_shxw(x,category,crawltime,y)
        if category == "要闻":
            list = data['trainArticles']['trainList']
            for y,x in enumerate(list):
                self.Analysis_shxw(x,category,crawltime,y)