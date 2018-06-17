from concurrent import futures
import requests
import os
import hashlib
import pymongo
import redis
import time
import pymysql
from util import *
from bs4 import BeautifulSoup
mongodb_client = pymongo.MongoClient(ConfigHelper.mongodbip, 27017)

def go(index):

    database = mongodb_client["crawlnews"]
    collection = database["runner_logs201805%02d" % index]
    collection2 = database["runner_logs201805%02d" % (index + 1)]
    # Created with Studio 3T, the IDE for MongoDB - https://studio3t.com/

    query = {}
    query["time"] = {
        u"$gt": u"2018-05-%02d" % (index + 1)
    }

    cursor = collection.find(query)
    try:
        for doc in cursor:

            collection2.insert(doc)

            print(doc)
        collection.remove(query)
    finally:
        mongodb_client.close()
if __name__ == '__main__':
    body = Http.get("http://zhuanlan.zhihu.com/p/34987004")
    # for index in range(4,31):
    #     go(index)
    index = 1
    database = mongodb_client["crawlnews"]
    collection = database["runner"]
    soup = BeautifulSoup(body, "html.parser")  # 文档对象
    # imgStrArr = soup.find_all('div', class_="Nfgz6aIyFCi3vZUoFGKEr")
    body = soup.find_all('body')
    print(body[0].text)

    sdata = {
        "title": "12312321321",
        "description": "21312323213313",
        "content": body[0].text,
        "source": "435345份453",
        "pubtimestr": "",
        "pubtime": "",
        "crawltimestr": "",
        "crawltime": "",
        "status": 0,
        "shorturl": "",
        "logo": "",
        "labels": "",
        "keyword": "",
        "seq": "",
        "identity": str(""),
        "appname": "",
        "app_tag": "",
        "category_tag": "",
        "category": "",
        "restype": "",
        "gallary": "",
        "video": "",
        "audio": ""
    }
    collection.insert(sdata)
    collection2 = database["runner_logs201806%02d" % index]
    # Created with Studio 3T, the IDE for MongoDB - https://studio3t.com/

    query = {}

    cursor = collection.find(query)
    try:
        for doc in cursor:
            collection2.insert(doc)

            print(doc)
    finally:
        mongodb_client.close()
    pass