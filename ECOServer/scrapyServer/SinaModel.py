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
from bs4 import BeautifulSoup
from util.log import SingleLogger
log = SingleLogger()

class SinaParse(BaseParse):
    # 解析新浪新闻
    def Analysis_sina(self,data,category, crawltime, y,categorytag):
        '''
        try:
            date = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))#当前时间
            f = open("E:\\" + category + date + ".txt",'a')
            f.write(json.dumps(data))
            f.close()
        except :
            print("文件未保存")
        '''

        title = ""  # 标题
        abstract = ""  # 摘要
        articleid = ""  # 文章标识
        tab = ""  # 标签
        source = ""  # 来源
        logo = ""  # 列表图片
        url = ""  # 文章短地址
        actionType = ""  # 文章展示类型（2-普通 14-头条 3-视频 1-广告 2-图片）
        layoutStyle = ""  # 布局样式
        publish_time = ""  # 发布时间 时间戳
        publish_timestr = ""  # 发布时间 标准时间str
        crawltimestr = ""  # 抓包时间
        restype = 1  # 类型 1 图文 2 图片 3 视频
        keywords = ""  # 关键字
        content = ""  # 内容
        gallary = ""  # 图片资讯图片地址

        # 文章展示类型（2-普通 14-头条 3-视频 1-广告 2-图片）
        actionType = data['actionType']

        # 标题
        try:
            if data['longTitle'] and data['longTitle'] != "":
                title = data['longTitle']
            elif data['title'] and data['title'] != "":
                title = data['title']
            else:
                SingleLogger.log.debug('无标题1')
        except:
            SingleLogger.log.debug('无标题2')

        # 发布时间
        try:
            publish_time = data['pubDate']
            if publish_time and publish_time != "":
                publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(publish_time))
        except:
            SingleLogger.log.debug("无发布时间")

        # 抓包时间
        try:
            crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))  # 抓包时间
        except:
            SingleLogger.log.debug("获取抓包时间失败")

        # 来源
        try:
            source = data['source']
        except:
            SingleLogger.log.debug("没有来源")

        # 短地址
        try:
            url = data['link']
        except:
            SingleLogger.log.debug("无短地址")

        # 文章标识
        try:
            articleid = data['newsId']
        except:
            SingleLogger.log.debug("没有文章标识")

        # 文章摘要
        try:
            abstract = data['intro']
        except:
            SingleLogger.log.debug('无摘要')

        # 列表图logo
        try:
            images = data['pics']['list']
            for imgobj in images:
                logo += imgobj['pic'] + "、"
        except:
            logo = data['pic']

        # 置顶
        try:
            if data['isTop'] and data['isTop'] == 1:
                if tab == "":
                    tab = "置顶"
                else:
                    tab += "、置顶"
        except:
            SingleLogger.log.debug('不置顶')

        # 分类处理
        # 视频
        if actionType == 3:
            SingleLogger.log.debug('视频')
            restype = 3
            # 防止报错
            try:
                videoInfo = data['videoInfo']  # 视频信息
                logo = videoInfo['pic']
                content = videoInfo['url']
            except:
                SingleLogger.log.debug("获取视频详情失败")

        # 图片
        elif actionType == 6:
            SingleLogger.log.debug('图片')
            restype = 2
            try:
                logo = data['pic']
                images = data['pics']['list']
                for imgobj in images:
                    gallary += imgobj['pic'] + "、"
                    content += imgobj['alt'] + "<br>"
            except:
                SingleLogger.log.debug('获取图片详情失败')

        # 广告
        elif actionType == 1:
            SingleLogger.log.debug('广告')
            if tab == "":
                tab = "广告"
            else:
                tab += "、广告"

        # 明日头条
        elif actionType == 14:
            SingleLogger.log.debug('明日头条')
            mrttList = data['mrttList']
            title = mrttList[0]['alt']
            logo = mrttList[0]['kpic']
            articleid = mrttList[0]['newsId']

        # 普通新闻
        else:
            SingleLogger.log.debug('普通新闻')
            # 防止报错
            if url != '':
                try:
                    gallary = self.getImg(url)
                except:
                    SingleLogger.log.debug("没有gallary")
                try:
                    content = self.getWen(url)
                except:
                    SingleLogger.log.debug("没有图文详情")
                try:
                    video = self.getVideo(url)
                    if video != '':
                        gallary += video
                except:
                    SingleLogger.log.debug("详情没有video")

        sdata = {
            "title": title,
            "description": abstract,
            "content": content,  #
            "source": source,
            "pubtimestr": publish_timestr,
            "pubtime": publish_time,
            "crawltimestr": crawltimestr,  # 抓包时间
            "crawltime": crawltime,
            "status": 0,
            "shorturl": url,
            "logo": logo,
            "labels": tab,
            "keyword": "",
            "seq": y + 1,  # 排序
            "identity": str(articleid),
            "appname": self.appname,
            "app_tag": self.apptag,
            "category_tag":categorytag,
            "category": category,  # 栏目
            "restype": restype,  #
            "gallary": gallary  # 里面的所有图片地址
        }
        self.db(sdata, articleid, title)

    # 获取图片main
    def getImgMain(self):
        html = rq.get(urls).text
        soup = BeautifulSoup(html, "html.parser")  # 文档对象
        imgStr = ""
        for k in soup.find_all('img'):  # 获取img
            imgStr += k['src'] + "、"
        return imgStr

    # 获取文字main
    def getWenMain(self):
        html = rq.get(urls).text
        soup = BeautifulSoup(html, "html.parser")  # 文档对象
        imgStrArr = soup.find_all('article', class_="art_box")
        if len(imgStrArr) == 0:
            return ''
        else:
            return imgStrArr[0]

    # 获取视频main
    def getVideoMain(self):
        html = rq.get(urls).text
        soup = BeautifulSoup(html, "html.parser")  # 文档对象
        imgStr = ""
        for k in soup.find_all('video'):
            imgStr += k['src'] + "、"
        return imgStr

    # 获取图片
    def getImg(self,link):
        global urls
        urls = link
        return self.getImgMain()

    # 获取图文
    def getWen(self,link):
        global urls
        urls = link
        return str(self.getWenMain())

    # 获取视频
    def getVideo(self,link):
        global urls
        urls = link
        return self.getVideoMain()

    def tryparse(self, str):
        # 转换编码格式
        strjson = str.decode("UTF-8", "ignore")
        # 转json对象
        strjson = json.loads(strjson)
        url = strjson['url']
        result = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(result.query, True)
        crawltime = strjson['time']

        # 区分栏目
        category = ""  # 类型
        category = params['channel'][0]
        if category == "news_jingyao":
            category = "要闻"
            categorytag = self.categroytag["%s" % category]
        elif category == "news_toutiao":
            category = "推荐"
            categorytag = self.categroytag["%s" % category]
        elif category == "news_video":
            category = "视频"
            categorytag = self.categroytag["%s" % category]
        elif category == "news_pic":
            category = "图片"
            categorytag = self.categroytag["%s" % category]
        else:
            SingleLogger.log.debug("有不正确的栏目")
            return

        # 获取data
        data = strjson['data']
        data = json.loads(data)
        # feed
        if data['data']['feed'] and data['data']['feed'] != '':
            feed = data['data']['feed']
            for y1, curobj1 in enumerate(feed):
                self.Analysis_sina(curobj1, category, crawltime, y1,categorytag)
        # ad
        try:
            if data['data']['ad']['feed'] and data['data']['ad']['feed'] != '':
                ad = data['data']['ad']['feed']
                for y2, curobj2 in enumerate(ad):
                    self.Analysis_sina(curobj2, category, crawltime, y2,categorytag)
        except:
            None