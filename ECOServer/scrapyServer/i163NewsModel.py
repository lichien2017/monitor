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
from util.log import Logger
log = Logger()

class WYNewsParse(BaseParse):
    # 解析网易新闻
    def Analysis_wyxw(self, data, category, crawltime, y):
        # try:
        #    date = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))#当前时间
        #    f = open("E:\\" + category + date + ".txt",'a')
        #    f.write(json.dumps(data))
        #    f.close()
        # except :
        #    print("文件未保存")
        title = ""  # 标题
        articleid = ""  # 文章标识
        restype = 1  # 类型 1 图文 2 图片 3 视频
        logo = ""  # 图片
        source = ""  # 来源
        abstract = ""  # 摘要
        content = ""  # 内容
        gallary = ""
        tab = ""  # 标签
        try:
            title = data['title']
        except:
            print("无title")
        publish_time = ""  # 发布时间
        publish_timestr = ""  # 发布时间戳
        if category == "视频":
            restype = 3
            abstract = data['description']
            logo = data['cover']
            source = data['topicName']
            articleid = data['vid']
        elif category == "图片":
            abstract = data['desc']
            publish_timestr = data['createdate']
            timeArray = time.strptime(publish_timestr, "%Y-%m-%d %H:%M:%S")
            publish_time = int(time.mktime(timeArray))
            title = data['setname']
            img_list = data['pics']
            for i in img_list:
                if i != "":
                    logo += i + ","
            url = data['seturl']
            articleid = data['setid']
            restype = 2
        else:
            try:
                abstract = data['digest']
            except:
                print("无digest")
            try:
                logo = data['imgsrc']
            except:
                print("无imgsrc")
            try:
                source = data['source']
            except:
                print("无source")
            try:
                if category == "问吧":
                    articleid = data['docid']
                else:
                    articleid = data['id']
            except:
                print("无id")
            # 若唯一标识为空，则获取图片唯一标识，此资讯为图片资讯
            if articleid == "":
                articleid = data['photosetID']
                restype = 2
            try:
                TAG = data['TAG']
                if TAG == "视频":
                    restype = 3
            except:
                print("无TAG")
            try:
                img_list = data['imgnewextra']
                for z in img_list:
                    if z['imgsrc'] != "":
                        logo += "," + z['imgsrc']
            except:
                print("仅一张或没有图片")
            try:
                tab = data['interest']
                if tab == "S":
                    tab = "置顶"
                else:
                    tab = ""
            except:
                print("无interest")
            if category == "热点":
                try:
                    tab = data['recReason']
                    if tab == "大家都在看":
                        tab = "热"
                    else:
                        tab = ""
                except:
                    print("无recReason")
        seq = y + 1  # 排序
        if publish_timestr == "":
            try:
                publish_timestr = data['ptime']
                timeArray = time.strptime(publish_timestr, "%Y-%m-%d %H:%M:%S")
                publish_time = int(time.mktime(timeArray))
            except:
                try:
                    publish_time = data['recTime']
                    publish_timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(publish_time))
                except:
                    print("无recTime、ptime")
        crawltimestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawltime / 1000))
        # 拼链接地址
        news_detail_url = 'https://c.m.163.com/nc/article/' + str(articleid) + '/full.html'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        # 若restype=3为视频资讯 取视频地址
        if restype == 3:
            url = 'https://c.m.163.com/nc/video/detail/' + str(articleid) + '.html'
            if category == "视频":
                content = data['mp4_url']
            elif category == "热点":
                news_detail = requests.get(url, headers=headers).json()
                content = news_detail['mp4_url']
            else:
                content = data['videoinfo']['mp4_url']
        elif restype == 2:
            if category == "图片":
                strarr = url.split('/')
                first = strarr[4][-4:]
                second = articleid
            else:
                strarr = articleid.split('|')
                first = strarr[0][-4:]
                second = strarr[1]
            news_detail_url = 'https://c.m.163.com/photo/api/set/' + str(first) + '/' + str(second) + '.json'
            news_detail = requests.get(news_detail_url, headers=headers).json()
            url = news_detail['url']
            tdata = news_detail['photos']
            for t in tdata:
                if t['imgurl'] != "":
                    gallary += t['imgurl'] + ","
                content += t['note'] + "<br/>"
        elif restype == 1:
            if category == "问吧":
                news_detail_url = 'https://wenba.m.163.com/wenda/mob/answer/detail.do?uuid=' + str(articleid)
                news_detail = requests.get(news_detail_url, headers=headers).json()['data']
                content = news_detail['answer']['content']
                # 读取问答图片
                image_list = news_detail['answer']['images']
                for i in image_list:
                    if i['src'] != "":
                        gallary += i['src'] + ","
                url = "https://c.m.163.com/news/ans/" + articleid + ".html"
                # 跟帖接口https://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/@replyid字段值/app/comments/newList
            else:
                try:
                    news_detail = requests.get(news_detail_url, headers=headers)
                    news_detail = news_detail.json()[str(articleid)]
                except:
                    time.sleep(20)
                    news_detail = requests.get(news_detail_url, headers=headers).json()[str(articleid)]
                # 读取资讯图片
                image_list = news_detail['img']
                for i in image_list:
                    if i['src'] != "":
                        gallary += i['src'] + ","
                # 读取资讯视频
                try:
                    video_list = news_detail['video']
                    for v in video_list:
                        if v['url_mp4'] != "":
                            gallary += v['url_mp4'] + ","
                except:
                    print("无视频")
                content = news_detail['body']
                # 读取
                try:
                    spinfo_list = news_detail['spinfo']
                    for s in video_list:
                        if s['spcontent'] != "":
                            content += v['spcontent']
                except:
                    None
                url = news_detail['shareLink']
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
            "appname": "网易新闻",
            "category": category,
            "restype": restype,
            "gallary": gallary
        }
        self.db(sdata, articleid, title)

    def tryparse(self, str):
        # 转换编码格式
        strjson = str.decode("UTF-8", "ignore")
        wdid = ""
        # 转json对象
        strjson = json.loads(strjson)
        url = strjson['url']
        result = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(result.query, True)
        if url.find('recommend/getSubDocPic') > -1:
            try:
                category = params['from'][0]
                if category == "toutiao":
                    category = "头条"
            except:
                category = "热点"
        elif url.find('recommend/getChanListNews') > -1:
            category = "视频"
        elif url.find('recommend/getComRecNews') > -1:
            wdidstr = url.split('?')[0].split('/')
            wdid = wdidstr[5]
            category = "问吧"
        elif url.find('recommend/useraction') > -1:
            if url.find('recommend/useraction?info=') > -1:
                print(url)
                return
            category = "两会"
        elif url.find('photo/api') > -1:
            # photo/api/set 为图片详情
            if url.find('photo/api/set') > -1:
                print(url)
                return
            category = "图片"
        else:
            return
        crawltime = strjson['time']
        # 获取data
        data = strjson['data']
        try:
            data = json.loads(data)
        except:
            print("无效抓取")
            return
        if category == "热点":
            list = data['推荐']
        elif category == "头条":
            list = data['tid']
        elif category == "视频":
            list = data['视频']
        elif category == "图片":
            list = data
        elif category == "问吧":
            list = data[wdid]
        for y, x in enumerate(list):
            self.Analysis_wyxw(x, category, crawltime, y)