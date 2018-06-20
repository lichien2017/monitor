# coding=utf-8
from scrapyServer.BaseModel import BaseParse

import json
from bs4 import BeautifulSoup
import time
from util import *

from util.log import SingleLogger


class ChangParse(BaseParse):
    # 解析畅读
    def Analysis_bdxw(self, data, category, crawltime, y, categorytag):
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 1  # 类型 1 图文 2 图片 3 视频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要(无摘要)
        tab = ""  # 标签
        gallary = "" #详情图片，视频
        content = ""  # 内容
        audio=''#音频
        video=''#视频

        dataitems = data['items'][0]
        publish_time = dataitems['time']
        url = dataitems['fileurl']
        content = self.getHtmlBodyInnerText(url)
        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(publish_time) / 1000))
        title = dataitems['title']
        source = dataitems['nickname']
        articleid = dataitems['id']
        gallary = self.getHtmlImages(url)
       # video = self.getHtmlVideos(url)
        logo = dataitems['img']
        # 判断图末尾是否为，若是则进行删除
        logolen = len(gallary)
        if logolen > 0:
            logostr = gallary[logolen - 1]
            if logostr == ",":
                gallary = gallary[:-1]


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
            "gallary": gallary,#里面的所有图片地址
            "video": video,
            "audio": audio
        }
        self.db(sdata, articleid, title)


    def getHtmlImages(self,url):
        html = Http.get(url)
        soup = BeautifulSoup(html, "html.parser")  # 文档对象
        imgStr = ""
        for k in soup.find_all('img'):  # 获取img
            try:
                imgStr += k['data-src'] + ","
            except:
                SingleLogger().log.debug("没有找到data-src标签")
            try:
                imgStr += k['src'] + ","
            except:
                SingleLogger().log.debug("没有找到src标签")
        return imgStr


    def tryparse(self, str):
        # 转换编码格式
        strjson = str.decode("UTF-8", "ignore")
        # 转json对象
        strjson = json.loads(strjson)
        url = strjson['url']
        #暂定只抓取精选
        category = "精选"
        categorytag = self.categroytag["%s" % category]

        crawltime = strjson['time']
        # 获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['data']['feedlist']

        for y, x in enumerate(list):
            self.Analysis_bdxw(x, category, crawltime, y,categorytag)
