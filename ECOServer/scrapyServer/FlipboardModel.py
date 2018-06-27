# coding=utf-8
from scrapyServer.BaseModel import BaseParse

import json
from bs4 import BeautifulSoup
import time
from util import *
from util.log import SingleLogger


class FlipboardParse(BaseParse):
    # 解析红板报
    def Analysis_bdxw(self, data, category, crawltime, y, categorytag):
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 1  # 类型 1 图文 2 图片 3 视频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        tab = ""  # 标签
        gallary = "" #详情图片，视频
        content = ""  # 内容
        audio=''#音频
        video=''#视频

        title = data['title']
        abstract = data['excerptText']
        url = data['sourceURL']
        articleid = data['id']

        publish_time = crawltime
        logo = data['inlineImage']['mediumURL']


        gallary = self.getHtmlImages(url)
        content = self.getHtmlBodyInnerText(url)

        # 判断图末尾是否为，若是则进行删除
        gallarylen = len(gallary)
        if gallarylen > 0:
            gallarystr = gallary[gallarylen - 1]
            if gallarystr == ",":
                gallary = gallary[:-1]


        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        SingleLogger().log.debug(title)
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

    def getHtmlImages(self, url):
        html = Http.get(url)
        soup = BeautifulSoup(html, "html.parser")  # 文档对象
        imgStr = ""
        for k in soup.find_all('img'):  # 获取img
            try:
                imgStr += k['data-src'] + ","
            except:
                SingleLogger().log.debug("没有找到标签")
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
        category = "首页"
        categorytag = self.categroytag["%s" % category]

        crawltime = strjson['time']
        # 获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['item']

        #for y, x in enumerate(list):
        self.Analysis_bdxw(list, category, crawltime, 0,categorytag)
