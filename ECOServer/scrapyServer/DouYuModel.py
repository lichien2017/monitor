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
class DouYuParse(BaseParse):

    # 解析斗鱼
    def Analysis_sntt(self,data, category, crawltime, y,categorytag,flag):
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 3  # 类型 1 图文 2 图片 3 视频 5音频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        tab = ""  # 标签
        keyword = ""  # 关键字
        gallary = ""
        content = ""  # 内容
        video = ''  # 视频
        audio = ''  # 音频
        url = ''  # 短地址
        publish_time = ''
        publish_timestr = ''
        submint = 0 # 是否集中提交
        crawltimestr = self.timeStr(crawltime)

        # 首页活动滚动图
        if flag == 0:
            title = data["act_name"]  # 标题
            articleid = data["id"]  # 文章标识
            restype = 1  # 类型 1 图文 2 图片 3 视频 5音频
            logo = data["room_src"]  # 图片
            abstract = data["act_info"]  # 摘要

            publish_time = data["act_start_time"]
            publish_timestr = self.timeStr(publish_time * 1000)
        # 热门推荐 或 推荐分类 或 颜值（高颜值主播推荐）或 推荐视频
        elif flag == 1:
            # 暂时斗鱼抓取到的标识都是1或3，要有其他的要另外分析是否结构一致
            if data["type"] == 1:
                try:
                    pos = data["pos"]
                    submint = 1  # 不集中提交
                    # 颜值（高颜值主播推荐)
                    for room in data["room"]:
                        title = room["room_name"]  # 标题
                        articleid = room["room_id"]  # 文章标识
                        logo = room["room_src"]  # 图片
                        source = room["nickname"]  # 来源
                        abstract = room["cate2_name"]  # 摘要
                        # 没有时间用抓取时间
                        publish_time = crawltime
                        publish_timestr = crawltimestr
                        try:
                            for key in room['atags']:
                                keyword += key['tag'] + ","
                        except:
                            print("没有关键字")
                        keyword = self.checkkeyword(keyword)
                        sdatas = self.sdata(title, abstract, content, source, publish_timestr, publish_time,
                                            crawltimestr, crawltime, url, logo, tab, keyword, seq, articleid,
                                            self.appname,
                                            self.apptag, categorytag, category, restype, gallary, video, audio)
                        self.db(sdatas, articleid, title)
                except:
                    # 热门推荐 或 推荐分类
                    room = data["room"]
                    title = room["room_name"]  # 标题
                    articleid = room["room_id"]  # 文章标识
                    logo = room["room_src"]  # 图片
                    source = room["nickname"]  # 来源
                    abstract = room["cate2_name"]  # 摘要
                    # 没有时间用抓取时间
                    publish_time = crawltime
                    publish_timestr = crawltimestr
                    try:
                        for key in room['atags']:
                            keyword += key['tag'] + ","
                    except:
                        print("没有关键字")
            elif  data["type"] == 3:
                # 推荐视频
                submint = 1  # 不集中提交
                for videos in data["videos"]:
                    title = videos["video_title"]  # 标题
                    articleid =  videos["point_id"]  # 文章标识
                    logo =  videos["video_cover"] # 图片
                    source =  videos["nickname"] # 来源
                    publish_time = videos["utime"]
                    publish_timestr = self.timeStr(publish_time * 1000)
                    sdatas = self.sdata(title, abstract, content, source, publish_timestr, publish_time,
                                        crawltimestr, crawltime, url, logo, tab, keyword, seq, articleid, self.appname,
                                        self.apptag, categorytag, category, restype, gallary, video, audio)
                    self.db(sdatas, articleid, title)
            else:
                print("类型不为Type：1 或 3")

        if submint == 0:
            keyword = self.checkkeyword(keyword)
            sdatas = self.sdata(title, abstract, content, source, publish_timestr, publish_time,
                                crawltimestr, crawltime, url, logo, tab, keyword, seq, articleid, self.appname,
                                self.apptag, categorytag, category, restype, gallary, video, audio)
            self.db(sdatas, articleid, title)

    # 判断关键字末尾是否为，若是则进行删除
    def checkkeyword(self, keyword):
        keywordlen = len(keyword)
        if keywordlen > 0:
            keywordstr = keyword[keywordlen - 1]
            if keywordstr == ",":
                keyword = keyword[:-1]
        return keyword

    def tryparse(self,str):
        # 转换编码格式
        strjson = str.decode("UTF-8", "ignore")
        # 转json对象
        strjson = json.loads(strjson)
        url = strjson['url']

        category = "推荐"
        categorytag = self.categroytag["%s" % category]

        crawltime = strjson['time']
        #获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['data']
        # 区分不同类型的标识
        flag = ""
        # 首页活动滚动图
        if url.find('apiv2.douyucdn.cn/Live/Subactivity/getActivityList') > -1:
            flag = 0
            list = data['data']['list']
        # 热门推荐 或 推荐分类
        elif url.find('apiv2.douyucdn.cn/mgapi/livenc/home/getRecList1') > -1:
            flag = 1
        # 颜值（高颜值主播推荐）或 推荐视频
        elif url.find('apiv2.douyucdn.cn/mgapi/livenc/home/getRecCardList') > -1:
            flag = 1

        for y,x in enumerate(list):
            self.Analysis_sntt(x,category,crawltime,y,categorytag,flag)

