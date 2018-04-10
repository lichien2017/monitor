# coding=utf-8
from BaseModel import BaseParse
import urllib.parse
import json
import requests
from pymongo import MongoClient
import time
import datetime
import hashlib
import uuid
import sys

class BaiDuParse(BaseParse):
    
    #解析百度新闻
    def Analysis_bdxw(self,data,category,crawltime,y):
        #try:
        #    date = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))#当前时间
        #    f = open("E:\\" + category + date + ".txt",'a')
        #    f.write(json.dumps(data))
        #    f.close()
        #except :
        #    print("文件未保存")
        seq = y + 1#排序
        title = ""#标题
        articleid = ""#文章标识
        restype = 1#类型 1 图文 2 图片 3 视频
        logo = ""#图片
        source = ""#来源
        abstract = ""#摘要
        tab=""#标签
        gallary = ""
        content=""#内容
        try:
            ctag=data['ctag']["name"]
            if ctag=="专题":
                return
            elif ctag=="置顶":
                tab=ctag
        except :
            print("无标签")
        title=data['title']
        abstract=data['abs']
        url=data['url']
        source=data['site']
        articleid=data['nid']
        publish_time=data['sourcets']
        img_url=data['imageurls']
        for i in img_url:
            if i['url']!="":
                logo+=i['url']+","
        try:
            corner_type=data['corner_type']
            if corner_type=="video":
                restype=3
                content=data['video']['url']
            elif corner_type=="image": 
                restype=2
        except :
            print("非视频/图片资讯")
        if restype!=3:
            content_data=data['content']
            for c in content_data:
                if c['type']=="image":
                    gallary +=c['data']['original']['url']+","
                elif c['type']=="text":
                    content+=c['data']+"<br/>"
        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(publish_time) / 1000))
        print(title)
        #判断列表封面图末尾是否为，若是则进行删除
        logolen=len(logo)
        if logolen>0:
            logostr=logo[logolen-1]
            if logostr==",":
                logo=logo[:-1]
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
            "appname": "百度新闻",
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
        if url.find('api/feed_feedlist') > -1:
            category = "推荐"
        elif url.find('api/newchosenlist') > -1:
            category = "视频"
        elif url.find('api/newslist') > -1:
            category = "两会"
        elif url.find('api/medianewslist') > -1:
            category = "图片"
        else:
            print(url)
            return
        crawltime = strjson['time']
        #获取data
        data = strjson['data']
        data=json.loads(data)
        list = data['data']
        if category=="推荐":
            data=list['top']
            for y,x in enumerate(data):
                self.Analysis_bdxw(x,category,crawltime,y)
            data=list['news']
            for y,x in enumerate(data):
                self.Analysis_bdxw(x,category,crawltime,y)
        else:
            data=list['news']
            datalen=len(data)
            for y,x in enumerate(data):
                #若类型等于图片时，则最后一次循环时进行跳出
                if category=="图片":
                   if datalen==y+1:
                        return
                self.Analysis_bdxw(x,category,crawltime,y)