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

class XiMaLaYaParse(BaseParse):
    # 解析喜马拉雅

    def Analysis_bdxw(self, data, category, crawltime, y, categorytag):
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 5  # 类型 1 图文 2 图片 3 视频 5音频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        tab = ""  # 标签
        keyword = "" #关键字
        gallary = ""
        content = ""  # 内容
        video = ''  # 视频
        audio = '' #音频
        url = '' #短地址
        publish_time = ''
        publish_timestr =''


        # 依据moduleType判断数据类型
        moduleType = data['moduleType']
        crawltimestr = self.timeStr(crawltime)

        # 板块 或 广告 或 电台 或 直播 或 为你推荐
        if moduleType =='square' or moduleType =='ad'\
                or moduleType == 'oneKeyListen' or moduleType == 'live'\
                or moduleType == 'recommendAlbum':
            # 不需要抓取
            return

        # 有特殊的关键字字段
        if moduleType == 'categoriesForShort' or moduleType == 'categoriesForLong'\
                or moduleType == 'categoriesForExplore':
            for key in data['keywords']:
                keyword += key['keywordName'] + ","
                print("=====keyword=======>%s" % keyword)
            # 判断关键字末尾是否为，若是则进行删除
            keywordlen = len(keyword)
            if keywordlen > 0:
                keywordstr = keyword[keywordlen - 1]
                if keywordstr == ",":
                    keyword = keyword[:-1]

        for c in data['list']:
            if moduleType != 'focus':
                # 猜你喜欢 或 精品(付费栏目) 或 最热有声书
                if moduleType == 'guessYouLike' or moduleType == 'paidCategory' or moduleType == 'categoriesForShort' or moduleType == 'categoriesForLong' or moduleType == 'categoriesForExplore':
                    try:
                        title = c['title']
                        articleid = c['albumId']
                        logo = c['pic']
                        source = c['nickname']
                        abstract = c['subtitle']
                        publish_time = c['lastUptrackAt']
                        publish_timestr = self.timeStr(publish_time)
                    except:
                        print("============>")
                # 轮播头条
                elif moduleType == 'topBuzz':
                    try:
                        title = c['title']
                        articleid = c['id']
                        logo = c['coverSmall']
                        source = c['nickname']
                        keyword = c['albumTitle']
                        audio = c['playPath32']
                        publish_time = c['updatedAt']
                        publish_timestr = self.timeStr(publish_time)
                    except:
                        print("======topBuzz======>")
                # 精品听单
                elif moduleType == 'playlist':
                    try:
                        title = c['title']
                        articleid = c['specialId']
                        logo = c['coverPath']
                        abstract = c['subtitle']
                        # 没有时间用抓取时间
                        publish_time = crawltime
                        publish_timestr = crawltimestr
                    except:
                        print("======playlist======>")
                # 听武汉
                elif moduleType == 'cityCategory':
                    try:
                        title = c['title']
                        articleid = c['albumId']
                        logo = c['pic']
                        source = c['nickname']
                        abstract = c['subtitle']
                        # 没有时间用抓取时间
                        publish_time = crawltime
                        publish_timestr = crawltimestr
                    except:
                        print("=====focus=======>")
                sdatas = self.sdata(title, abstract, content, source, publish_timestr, publish_time,
                                    crawltimestr, crawltime, url, logo, tab, keyword, seq, articleid, self.appname,
                                    self.apptag, categorytag, category, restype, gallary, video, audio)
                self.db(sdatas, articleid, title)
            # 轮播图（结构不一致单独写）
            else:
                # 轮播图无标题
                title = '喜马拉雅轮播图标题'
                for l in c['data']:
                    try:
                        articleid = l['adId']
                        logo = l['cover']
                        # 没有时间用抓取时间
                        publish_time = crawltime
                        publish_timestr = crawltimestr
                    except:
                        print("=====cityCategory=======>")
                    sdatas = self.sdata(title, abstract, content, source, publish_timestr, publish_time,
                                        crawltimestr, crawltime, url, logo, tab, keyword, seq, articleid, self.appname,
                                        self.apptag, categorytag, category, restype, gallary, video, audio)
                    self.db(sdatas, articleid, title)





    def tryparse(self, str):
        # 转换编码格式
        strjson = str.decode("UTF-8", "ignore")
        # 转json对象
        strjson = json.loads(strjson)
        # 暂时只取这一个栏目
        category = "推荐"
        categorytag = self.categroytag["%s" % category]

        crawltime = strjson['time']
        # 获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['list']
        for y, x in enumerate(list):
            self.Analysis_bdxw(x, category, crawltime, y,categorytag)