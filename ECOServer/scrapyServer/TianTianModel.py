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
log = SingleLogger()
class TianTianParse(BaseParse):

    #解析天天快报
    def Analysis_ttkb(self,data,category,crawltime,y,categorytag):
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
        articleid = data['id']
        title = data['title']
        try:
            source = data['source']
        except:
            SingleLogger.log.debug("无source")
        abstract = data['abstract']
        articletype = data['articletype']
        try:
            stick = data['stick']
            if stick == 1:
                tab = "置顶"
                if articletype == "100":
                     tab+="、专题"
        except:
            SingleLogger.log.debug("非置顶资讯")
        if category=="热点":
            flag=data['flag']
            if flag=="17":
                tab="首发"
            elif flag=="18":
                tab="独家"
        try:
            img_list = data['img_face']
            #列表页存在多个图片 奇数与偶数一致，取偶数图片地址
            for z,i in enumerate(img_list):
                if (z + 1) % 2 == 0:
                     if i != "":
                        logo+=i + ","
        except:
            try:
                img_list = data['thumbnails']
                for i in img_list:
                    if i != "":
                        logo+=i + ","
            except:
                SingleLogger.log.debug("无图片")
        gallary_list = data['thumbnails_qqnews']
        for g in gallary_list:
            if g != "":
                gallary+=g + ","
        if category!="视频":
            try:
                hasVideo = data['hasVideo']
                if hasVideo == 1:
                    restype = 3
            except:
                SingleLogger.log.debug("无hasVideo")
        else:
             restype = 3
        if articletype == "12" or articletype == "1":#图文资讯
            restype = 2
        elif articletype == "30":#广告
            IsArtID = True
        url = data['short_url']
        publish_timestr = data['time']
        timeArray = time.strptime(publish_timestr, "%Y-%m-%d %H:%M:%S")
        publish_time = int(time.mktime(timeArray))
        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        if restype != 3 and IsArtID == False:
            if tab.find('专题') > -1:
                content = url
            else:
                #拼链接地址
                news_detail_url = 'http://r.cnews.qq.com/getSubNewsContent'
                headers = {'idfa':'41197B17-583C-4A36-93DF-2C2C19137A7A',
                           'deviceToken':'<f30ebcd9 220eb545 eed63639 34ddc3eb f45bc81d eea5346a 6db51e26 f8ead8df>',
                           'qn-rid':'51E553EE-52F1-4B7E-BB88-C14E28CB6CC2',
                           'qn-sig':'DABA48EC29C64749BA6CF95F725EA249',
                           'appver':'11.2.6_qnreading_4.6.70',
                           'apptypeExt':'qnreading',
                           'devid':'8DB8C30D-28EC-440F-9AD2-8BBC2D477A95'}
                postData = {'id':str(articleid)}
                #返回文章json
                news_detail = requests.post(news_detail_url,data=postData,headers=headers).json()
                content = news_detail['content']['text']
                #读取详情非文字的附件
                attribute = news_detail['attribute']
                for a in attribute:
                    try:
                        #判断gallary是否存在此链接地址，存在则跳出此次循环，不存在则进行拼接
                        if gallary.find(attribute[a]["url"]) > -1:
                            continue
                        else:
                            gallary+=attribute[a]["url"] + ","
                    except:
                        try:
                            gallary+=attribute[a]["playurl"] + ","
                        except:
                            try:
                                gallary+=attribute[a]["murl"] + ","
                            except:
                                SingleLogger.log.debug(json.dumps(attribute))
                if category == "问答":
                    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
                    news_detail_url = 'https://r.cnews.qq.com/getQQNewsComment'
                    comment_id = data['commentid']
                    postData = {'comment_id':str(comment_id),'article_id':str(articleid),'chlid':'kb_news_qna','c_type':'qa'}
                    #返回文章json
                    news_detail = requests.post(news_detail_url,data=postData).json()['comments']
                    comdata =news_detail['new']
                    for c in comdata:
                        content+=c[0]['reply_content'] + "<br/>"
                        #读取评论非文字的附件
                        try:
                            attribute = c[0]['attribute']
                            for a in attribute:
                                try:
                                    #判断gallary是否存在此链接地址，存在则跳出此次循环，不存在则进行拼接
                                    if gallary.find(attribute[a]["url"]) > -1:
                                        continue
                                    else:
                                        gallary+=attribute[a]["url"] + ","
                                except:
                                    try:
                                        gallary+=attribute[a]["playurl"] + ","
                                    except:
                                        try:
                                            gallary+=attribute[a]["murl"] + ","
                                        except:
                                            SingleLogger.log.debug(json.dumps(attribute))
                        except:
                            None

        elif restype==3:
             content = data['video_channel']['video']['playurl']#视频地址
        #判断列表封面图末尾是否为，若是则进行删除
        logolen = len(logo)
        if logolen > 0:
            logostr = logo[logolen - 1]
            if logostr == ",":
                logo = logo[:-1]
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
            "appname": self.appname,
            "app_tag": self.apptag,
            "category_tag":categorytag,
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
        post = strjson['post']
        if url.find('getSubNewsInterest') > -1:
            category = "推荐"
        elif url.find('getSubNewsChlidInterest') > -1:
            chlid = ""
            params = post.split('&')
            for p in params:
                if p.find('chlid') > -1:
                    chlid = p.split('=')[1]
                    break
            if chlid == "kb_news_lianghui":
                category = "两会"
                categorytag = self.categroytag["%s" % category]
            elif chlid == "kb_video_news":
                category = "视频"
                categorytag = self.categroytag["%s" % category]
            elif chlid == "kb_news_hotnews":
                category = "热点"
                categorytag = self.categroytag["%s" % category]
            elif chlid == "kb_news_qna":
                category = "问答"
                categorytag = self.categroytag["%s" % category]
            elif chlid == "kb_photo_news":
                category = "图片"
                categorytag = self.categroytag["%s" % category]
            else:
                SingleLogger.log.debug(post)
                return
        else :
             SingleLogger.log.debug(url)
             return
        crawltime = strjson['time']
        #获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['newslist']
        for y,x in enumerate(list):
            self.Analysis_ttkb(x,category,crawltime,y,categorytag)
