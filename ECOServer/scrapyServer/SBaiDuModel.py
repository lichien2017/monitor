# coding=utf-8
from scrapyServer.BaseModel import BaseParse
import json
import urllib
from util.log import SingleLogger
class SBaiDuParse(BaseParse):

    # 解析百度搜索
    def Analysis_sntt(self,data, category, crawltime, y,categorytag):
        seq = y + 1  # 排序
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 1  # 类型 1 图文 2 图片 3 视频 5音频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        tab = ""  # 标签
        keywords = ""  # 关键字
        gallary = ""
        content = ""  # 内容
        video = ''  # 视频
        audio = ''  # 音频
        url = ''  # 短地址
        publish_time = ''
        publish_timestr = ''

        crawltimestr = self.timeStr(crawltime)
        layout = data["layout"]

        articleid = data["id"]  # 文章标识
        data = data["data"]

        if data["mode"] == 'video':
            restype = 3
        elif data["mode"] == 'image':
            restype = 2
        elif data["mode"] == 'text':
            restype = 1
        elif data["mode"] == 'ad':
            # 广告
            return
        else:
            SingleLogger().log.debug("无法识别数据类型")
            return ;



        try:
            title = data["title"]  # 标题
            if layout != "titleonly":
                if data["prefetch_image"] =="":
                    logo = data["image"]  # 图片
                else:
                    logo = data["prefetch_image"]  # 图片
            source = data["source"]  # 来源


            if layout == "autovideo" or data["mode"] == 'video':
                try:
                    video = data["video"]  # 视频
                    url = data["videoInfo"]["pageUrl"]  # 短地址
                except:
                    video = data["prefetch_video"][0]["url"]  # 视频
                    url =  video # 短地址
                content = title
            elif  data["mode"] == 'image':
                content = title
                for imgitems in data["items"]:
                    if imgitems['img'] != "":
                        gallary += imgitems['image'] + ","
            else:
                url = data["prefetch_html"]  # 短地址
                content = self.getHtmlBodyInnerText(url)
                gallary = self.getHtmlImages(url)

            publish_time = crawltime
            publish_timestr = crawltimestr

        except:
            SingleLogger().log.debug("数据解析错误")

        # 判断封面图末尾是否为，若是则进行删除
        logolen = len(logo)
        if logolen > 0:
            logostr = logo[logolen - 1]
            if logostr == ",":
                logo = logo[:-1]

        gallarylen = len(gallary)
        if gallarylen > 0:
            gallarystr = gallary[gallarylen - 1]
            if gallarystr == ",":
                gallary = gallary[:-1]
        sdatas = self.sdata(title, abstract, content, source, publish_timestr, publish_time,
                            crawltimestr, crawltime, url, logo, tab, keywords, seq, articleid, self.appname,
                            self.apptag, categorytag, category, restype, gallary, video, audio)
        self.db(sdatas, articleid, title)





    def tryparse(self,str):
        # 转换编码格式
        strjson = str.decode("UTF-8", "ignore")
        # 转json对象
        strjson = json.loads(strjson)
        url = strjson['url']
        category = "推荐"

        categorytag = self.categroytag["%s" % category]
        crawltime = strjson['time']

        if url.find('action=feed&cmd=100&service=bdbox') >-1:
            #获取data
            data = strjson['data']
            data = json.loads(data)
            try:
                items = data['data']['100']["itemlist"]['items']
            except:
                SingleLogger().log.debug("无数据获取")

            for y,x in enumerate(items):
                self.Analysis_sntt(x,category,crawltime,y,categorytag)

        else:
            return ;