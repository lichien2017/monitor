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
class ToutiaoParse(BaseParse):
    # def __init__(self,name):
    #     BaseModel.BaseParse.__init__(self,name)

    # 解析今日头条
    def Analysis_sntt(self,x, category, crawltime, y,categorytag):
        data = x['content']
        #try:
        #    date = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))#当前时间
        #    f = open("E:\\" + category + date + ".txt",'a')
        #    f.write(data)
        #    f.close()
        #except :
        #    print("文件未保存")
        data = json.loads(data)
        title = ""#标题
        articleid = ""#文章标识
        restype = 1#类型 1 图文 2 图片 3 视频
        logo = ""#图片
        source = ""#来源
        abstract=""#摘要
        try:
            abstract = data['abstract']#摘要
        except:
            SingleLogger().log.debug("无摘要")
        seq = y+1#排序
        keywords = ""#关键字
        gallary = ""#图片资讯图片地址
        IsV = False#是否为大V资讯
        IsArtID=False#是否无唯一标识，并为广告
        url=""#资讯地址
        content=""#内容
        publish_time = ""#发布时间
        publish_timestr=""#发布时间 标准时间
        hot=0#是否为热门
        tab = ""#标签
        try:
            tab = data['label']
        except:
            tab = ""
            SingleLogger().log.debug("非置顶文章")
        try :
            url = data['display_url']#分享地址
        except:
            try:
                url = data['share_url']#分享地址
            except:
                try:
                    url = data['url']#分享地址
                except:
                    SingleLogger().log.debug("无资讯地址")
        try:
            publish_time = data['publish_time']
        except:
            SingleLogger().log.debug("无发布时间")
        #如果是美图栏目
        if category == "美图":
            try:
                title = data['content']
            except:
                SingleLogger().log.debug("无内容仅只有图片")
            articleid = data['group_id']#文章标识
            logo = data['large_image']['url']
            publish_time = data['create_time']
        #如果是小视频栏目
        elif category == "小视频":
            xdata=data['raw_data']
            title = xdata['title']
            articleid = xdata['group_id']
            image_list = xdata['large_image_list']
            for w in image_list:
                if w['url']!="":
                    logo+=w['url']+","
            url=xdata['share']['share_url']
            publish_time=xdata['create_time']
            restype = 3
        #如果是问答栏目
        elif category == "问答":
            seq=y
            try:
                qdata=data['question']
                qdata=json.loads(qdata)#转json
                title = qdata['title']
                articleid = qdata['qid']
                publish_time=qdata['create_time']
                image_list = qdata['content']['large_image_list']
                for w in image_list:
                    if w['url']!="":
                        logo+=w['url']+","
            except:
                return
        else:
            try:
                title = data['title']
            except :
                SingleLogger().log.debug("无标题")
            try:
                articleid = data['group_id']#文章标识
            except :
                try:
                    articleid = data['thread_id']#文章标识
                    IsV = True
                    try:
                        #取文章图片列表
                        large_image_list = data['large_image_list']
                        for i,j in enumerate(large_image_list):
                            if j['url']!="":
                                #取前3个图为列表图
                                if(i < 3):
                                    logo+=j['url'] + ","
                                gallary+=j['url'] + ","
                    except :
                        SingleLogger().log.debug("大V资讯无图片")
                except :
                    #若此资讯是广告，并无唯一标识，则生成一个唯一标识
                    if tab=="广告":
                        articleid=uuid.uuid1()#文章标识
                        IsArtID=True
                    SingleLogger().log.debug("无唯一标识：")
            #如果has_video=true 则为视频新闻
            if data['has_video'] == True:
                restype = 3
            else:
                 try:
                    keywords = data['keywords']#关键字
                 except :
                    SingleLogger().log.debug("无关键字")
            try:
                logo = data['middle_image']['url']
            except:
                SingleLogger().log.debug("无封面图")
        #如果文章标识为空，则跳出此循环
        if articleid == "":
            return
        try:
            source = data['source']
        except :
            SingleLogger().log.debug("无来源")
        #是否为图片新闻
        try:
            gallary_flag = data['gallary_flag']
            if gallary_flag == 1:
                restype = 2
        except:
            SingleLogger().log.debug("非图片新闻")
        try:
            hot = data['hot']#0 非热门 1 热门
        except:
            SingleLogger().log.debug("非热门")
        if hot == 1:
            if tab == "":
                tab = "热"
            else:
                tab = tab + "、热"
        #若restype=1为普通资讯 则可能存在多张图片
        if restype == 1:
            try:
                image_list = data['image_list']
                logo = ""
                for i in image_list:
                    if i['url']!="":
                        logo+=i['url'] + ","
            except:
                SingleLogger().log.debug("只一张或没有图片")
        if publish_time!="":
            publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(publish_time))
        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        #不为广告并有唯一标识 则取资讯详情信息
        if IsArtID==False:
            if category == "问答":
                news_detail_url='http://is.snssdk.com/wenda/v2/question/brow/?device_id=48679316565'
                postData = {'qid':str(articleid),'count':30}
                #返回文章json
                news_detail = requests.post(news_detail_url,data=postData).json()
                qdata=news_detail['question']
                content=qdata['content']['text']
                url=qdata['share_data']['share_url']#分享地址
                adata=news_detail['data']
                gallary=""
                for a in adata:
                    content+="<br/>"+a['answer']['content_abstract']['text']
                    image_list = a['answer']['content_abstract']['large_image_list']
                    for w in image_list:
                        if w['url']!="":
                            gallary+=w['url']+","
                articleid=uuid.uuid1()#文章标识
            else:
                #拼链接地址
                news_detail_url = 'http://a3.bytecdn.cn/article/content/15/2/' + str(articleid) + '/' + str(articleid) + '/1/'
                if IsV:
                    news_detail_url = 'http://lf.snssdk.com/ugc/thread/detail/v2/content/?thread_id=' + str(articleid)
                    #返回文章json
                    news_detail =requests.get(news_detail_url).json()
                else:
                    #返回文章json
                    news_detail = requests.get(news_detail_url).json()['data']
                try:
                    content = news_detail['content']
                    #若restype=2为图片新闻 则取图片地址
                    if restype == 2:
                        gallery = news_detail['gallery']
                        for z in gallery:
                            gallary+=z['sub_image']['url'] + ","
                except:
                    SingleLogger().log.debug("内容暂无/图片取值错误")
        sdata={
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
            "keyword": keywords,
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
        # 转换编码格式
        strjson = str.decode("UTF-8", "ignore")
        # 转json对象
        strjson = json.loads(strjson)
        url = strjson['url']
        result = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(result.query,True)
        category = ""#类型
        try:
            category = params['category'][0]
            if category == "news_hot":
                category = "热点"
                categorytag = self.categroytag["%s" % category]
            elif category == "hotsoon_video":
                category = "小视频"
                categorytag = self.categroytag["%s" % category]
            elif category == "video":
                category = "视频"
                categorytag = self.categroytag["%s" % category]
            elif category == "组图":
                category = "图片"
                categorytag = self.categroytag["%s" % category]
            elif category == "image_wonderful":
                category = "美图"
                categorytag = self.categroytag["%s" % category]
        except :
            if url.find('wenda/v1/native/feedbrow') > -1:
                category = "问答"
                categorytag = self.categroytag["%s" % category]
            else:
                category = "推荐"
                categorytag = self.categroytag["%s" % category]
                SingleLogger().log.debug("无类型")
        if category != "两会" and category != "问答" and category != "热点" and category != "视频" and category != "小视频" and category != "推荐" and category != "图片" and category != "美图":
           return
        crawltime = strjson['time']
        #获取data
        data = strjson['data']
        data = json.loads(data)
        list = data['data']
        for y,x in enumerate(list):
            self.Analysis_sntt(x,category,crawltime,y,categorytag)

