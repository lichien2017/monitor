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

class DeDaoParse(BaseParse):
    # 解析得到
    def Analysis_bdxw(self, data, category, crawltime, y, categorytag,flag):
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 5  # 类型 1 图文 2 图片 3 视频 5音频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        tab = ""  # 标签
        gallary = ""
        content = ""  # 内容
        video = ''  # 视频
        audio = '' #音频
        url = ''  # 短地址
        keyword = ""  # 关键字
        publish_time = ''
        publish_timestr = ''
        crawltimestr = self.timeStr(crawltime)


        if flag != 1:
            #轮播图
            if flag == 0:
                title = data["m_title"]
                articleid = data["log_id"]  # 文章标识
                restype = 1
                logo = data["m_img"]
                url = data["m_url"]  # 短地址
                # 没有时间用抓取时间
                publish_time = crawltime
                publish_timestr = crawltimestr
                content = self.getHtmlBodyInnerText(url)
                gallary = self.getHtmlImages(url)
            # 每天听本书
            if flag == 2:
                restype = 1  # 类型
                articleid = data["id"]  # 文章标识
                content = data["audio_brife"]  # 内容
                audio_detail = data["audio_detail"]
                title = audio_detail["title"]  # 标题
                logo = audio_detail["icon"]  # 图片
                source = audio_detail["source_name"]  # 来源
                abstract = audio_detail["share_summary"]  # 摘要
                audio = audio_detail["mp3_play_url"]  # 音频
                # 没有时间用抓取时间
                publish_time = crawltime
                publish_timestr = crawltimestr
            # 订阅专栏/大师课
            if flag == 3:
                title = data["title"]  # 标题
                articleid = data["id"]  # 文章标识
                restype = 1  # 类型 1 图文 2 图片 3 视频 5音频
                logo = data["logo"]  # 图片
                abstract = data["intro"] + data["article_title"] # 摘要
                content = data["notice"] + data["consumer"] # 内容
                url = data["shzf_url"]  # 短地址
                publish_time = data["article_time"]
                publish_timestr = self.timeStr(publish_time * 1000)
            # 猜你喜欢
            if flag == 4:
                title = data["m_title"]  # 标题
                articleid = data["m_id"]  # 文章标识
                restype = 1  # 类型 1 图文 2 图片 3 视频 5音频
                logo = data["m_img"]  # 图片
                # 没有时间用抓取时间
                publish_time = crawltime
                publish_timestr = crawltimestr
            # 精品课
            if flag == 5:
                title = data["title"]  # 标题
                articleid = data["id"]  # 文章标识
                restype = 1 # 类型 1 图文 2 图片 3 视频 5音频
                logo = data["homepage_img"]  # 图片
                abstract = data["sub_title"]  # 摘要
                publish_timestr = data["lecturer"]["udt"]
                timeArray = time.strptime(publish_timestr, "%Y-%m-%d %H:%M:%S")
                publish_time = int(time.mktime(timeArray))  # string转成时间戳
            # 底部介绍
            if flag == 6:
                title = data["m_title"]  # 标题
                articleid = data["log_id"]  # 文章标识
                restype = 1  # 类型 1 图文 2 图片 3 视频 5音频
                logo = data["m_img"] # 图片
                url = data["m_url"]  # 短地址
                content = self.getHtmlBodyInnerText(url)
                gallary = self.getHtmlImages(url)
                # 没有时间用抓取时间
                publish_time = crawltime
                publish_timestr = crawltimestr



            # 判断gallary末尾是否为，若是则进行删除
            gallarylen = len(gallary)
            if gallarylen > 0:
                gallarystr = gallary[gallarylen - 1]
                if gallarystr == ",":
                    gallary = gallary[:-1]

            sdatas = self.sdata(title, abstract, content, source, publish_timestr, publish_time,
                                crawltimestr, crawltime, url, logo, tab, keyword, seq, articleid, self.appname,
                                self.apptag, categorytag, category, restype, gallary, video, audio)

            self.db(sdatas, articleid, title)


        # 免费专区
        else:
            for c in data['audio_list']:
                publish_time = c["publish_time_stamp"]
                publish_timestr = self.timeStr(publish_time * 1000)
                articleid = c["id"] # 文章标识
                audio_detail = c["audio_detail"]
                source = audio_detail["source_name"] # 来源
                title = audio_detail["title"]  # 标题
                logo = audio_detail["icon"]  # 图片
                abstract = audio_detail["share_summary"]  # 摘要
                audio = audio_detail["mp3_play_url"]  # 音频
                sdatas = self.sdata(title, abstract, content, source, publish_timestr, publish_time,
                                    crawltimestr, crawltime, url, logo, tab, keyword, seq, articleid, self.appname,
                                    self.apptag, categorytag, category, restype, gallary, video, audio)

                self.db(sdatas, articleid, title)




    def tryparse(self, str):
        # 转换编码格式
        strjson = str.decode("UTF-8", "ignore")
        # 转json对象
        strjson = json.loads(strjson)
        url = strjson['url']
        # 暂时只取这一个栏目
        category = "发现"
        categorytag = self.categroytag["%s" % category]
        crawltime = strjson['time']
        data = strjson['data']
        data = json.loads(data)
        try:
            list = data['c']['list']
        except:
            list = data['c']['data']['data']
        # 区分不同类型的标识
        flag = ""
        # 轮播图
        if url.find('dedao.igetget.com/v3/adv/homepage') > -1:
            flag = 0
        # 免费专区
        elif url.find('entree.igetget.com/acropolis/v1/column/homepage') > -1:
            flag = 1
        # 每天听本书
        elif url.find('entree.igetget.com/odob/v2/app/homepage') > -1:
            flag = 2
            self.Analysis_bdxw(list, category, crawltime, 0, categorytag, flag)
        # 订阅专栏
        elif url.find('entree.igetget.com/parthenon/v1/column/homepage') > -1:
            flag = 3
        # 大师课
        elif url.find('entree.igetget.com/erechtheion/v1/master/homepage') > -1:
            flag = 3
        # 猜你喜欢
        elif url.find('dedao.igetget.com/v3/datamining/homepage') > -1:
            flag = 4
        # 精品课
        elif url.find('entree.igetget.com/noa/course/coursedetail/directstructuredata') > -1:
            flag = 5
        # 底部介绍
        elif url.find('dedao.igetget.com/v3/adv/homesubject') > -1:
            flag = 6
        else:
            SingleLogger().log.debug(url)
            return

        if flag !=2:
            for y, x in enumerate(list):
                self.Analysis_bdxw(x, category, crawltime, y, categorytag,flag)