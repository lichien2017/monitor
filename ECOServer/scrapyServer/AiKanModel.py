# coding=utf-8
from scrapyServer.BaseModel import BaseParse
import json
from util.log import SingleLogger
class AiKanParse(BaseParse):

    # 解析爱看
    def Analysis_sntt(self,x, category, crawltime, y,categorytag):
        data = x['content']
        data = json.loads(data)
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

        # 如果是横排滑动样式的视频，格式不一样要区分处理
        try:
            for videodata in data['data']:
                restype = 3
                articleid = videodata["id"]
                raw_data = videodata["raw_data"]
                try:
                    for c in raw_data["animated_image_list"]:
                        logo += c["url"] + ","
                except:
                    SingleLogger().log.debug("暂无封面图")
                publish_time = raw_data["create_time"]
                publish_timestr = self.timeStr(publish_time * 1000)
                title = raw_data["title"]  # 标题
                url = raw_data["share"]["share_url"]  # 短地址
                content = self.getHtmlBodyInnerText(url)
                gallary = self.getHtmlImages(url)
                # 判断封面图末尾是否为，若是则进行删除
                logolen = len(logo)
                if logolen > 0:
                    logostr = logo[logolen - 1]
                    if logostr == ",":
                        logo = logo[:-1]
                sdatas = self.sdata(title, abstract, content, source, publish_timestr, publish_time,
                                    crawltimestr, crawltime, url, logo, tab, keywords, seq, articleid, self.appname,
                                    self.apptag, categorytag, category, restype, gallary, video, audio)
                self.db(sdatas, articleid, title)
        except:
            title = data['title']  # 标题
            abstract = data["abstract"]
            articleid = data["rid"]  # 文章标识
            source = data["source"]  # 来源
            url = data["url"]  # 短地址
            publish_time = data["publish_time"]
            publish_timestr = self.timeStr(publish_time * 1000)
            content = self.getHtmlBodyInnerText(url)
            gallary = self.getHtmlImages(url)
            try:
                keywords = data["keywords"]
            except:
                SingleLogger().log.debug("暂无关键字")

            # 是否有视频文件
            if data["has_video"]:
                restype = 3
            try:
                for c in  data["image_list"]:
                    logo += c["url"] + ","
            except:
                SingleLogger().log.debug("image_list暂无封面图")

            try:
                for c in data["large_image_list"]:
                    logo += c["url"] + ","
            except:
                SingleLogger().log.debug("large_image_list暂无封面图")


            # 判断封面图末尾是否为，若是则进行删除
            logolen = len(logo)
            if logolen > 0:
                logostr = logo[logolen - 1]
                if logostr == ",":
                    logo = logo[:-1]
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
        #获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['data']
        for y,x in enumerate(list):
            self.Analysis_sntt(x,category,crawltime,y,categorytag)

