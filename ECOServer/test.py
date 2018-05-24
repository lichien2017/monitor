
from concurrent import futures
import requests
import os
import hashlib
import pymongo
import redis
import time
import pymysql
from util import *
from mysqldb.mysql_helper import MySQLHelper

import json
import datetime


from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    imgs = []
    def handle_starttag(self, tag, attrs):
        if tag == "img":
            for attr in attrs:
                if attr[0] == 'src':
                    if attr[1] == '/uploads/allimg/180426/3-1P42609444K91.jpg':
                        print("Encountered a start attrs:", attr[1])

                    self.imgs.append(attr[1])


    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        pass

    def handle_data(self, data):
        pass
        #print("Encountered some data  :", data)

log = Logger()
# 设定ThreadPoolExecutor 类最多使用几个线程
MAX_WORKERS = 10
# 图片保存地址
DEST_DIR = '/Users/lizhengqing/Documents'   # "/mnt/download_media/"
print(DEST_DIR)
# mongodb
mongodb_client = pymongo.MongoClient(ConfigHelper.mongodbip, 27017)
# redis
pool = redis.ConnectionPool(host=ConfigHelper.redisip, port=6379, db=ConfigHelper.redisdb)
redis_server = redis.StrictRedis(connection_pool=pool)


# 对url进行md5编码作为图片的文件名
def get_md5(url):
    m = hashlib.md5()
    m.update(url.encode("utf-8"))
    return m.hexdigest()

# 保存图片
def save_image(img, url):  # <5>
    index = url.rfind('/')
    part_path = url[0:index]
    path = DEST_DIR +  part_path
    if not os.path.exists(path):
        os.makedirs(path)
    full_filename = DEST_DIR + url

    if not os.path.exists(full_filename):
        with open(full_filename, 'wb') as fp:
            fp.write(img)



def get_image(url):  # <6>
    if url.startswith("file:///") :
        return None
    if not url.startswith('http://'):
        url = 'http://www.hbjsxrmyy.com/'+ url
    resp = requests.get(url)
    if resp.status_code != 200:  # <1>
        resp.raise_for_status() # 如果不是200 抛出异常
    return resp.content

def download_one(url):
    try:
        image = None
        full_filename = DEST_DIR + url
        if not os.path.exists(full_filename):
            image = get_image(url)
    # 捕获 requests.exceptions.HTTPError
    except requests.exceptions.HTTPError as exc:  #
        # 如果有异常 直接抛出
        raise
    else:
        if image != None :
            save_image(image, url)
    return url



def download_many(cc_list):
    # cc_list = cc_list[:5]
    #with futures.ProcessPoolExecutor() as executor:
    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        to_do_map = {}
        for cc in cc_list:
            # if cc == None or cc == "" :
            #     continue
            future = executor.s(download_one, cc)
            to_do_map[future] = cc
            msg = 'Scheduled for {}: {}'
            log.debug(msg.format(cc, future))

        results = []
        for future in futures.as_completed(to_do_map):
            try:
                res = future.result()
            except requests.exceptions.HTTPError as exc:
                # 处理可能出现的异常
                error_msg = '{} result {}'.format(cc, exc)
            else:
                error_msg = ''
            if error_msg:
                cc = to_do_map[future]  # <16>
                log.error('*** Error for {}: {}'.format(cc, error_msg))
            else:
                msg = '{} result: {!r}'
                log.debug(msg.format(future, res))
                results.append(res)

    return len(results)



def download_files():
    conn = MySQLHelper.pool_connection.get_connection()
    # 创建游标
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    # 执行SQL，并返回收影响行数
    row_count = cursor.execute("""
                    select litpic,body
from `yw_archives` a left join `yw_addonarticle` b on a.id = b.aid
               where body != null or body != ''  order by a.id desc """ )

    result = cursor.fetchone()
    parser = MyHTMLParser()
    jobs = []
    count = 0
    while result != None:
        #jobs.append(result["litpic"])
        parser.feed(result["body"])
        for u in parser.imgs :
            log.debug(u)
            try:
                if u == '/uploads/allimg/180316/3-1P316160S9138.jpg':
                    download_one(u)
            except Exception as e:
                log.error(e)
        #jobs=jobs+parser.imgs
        count = count + len(parser.imgs)
        # download_many(parser.imgs)
        result = cursor.fetchone()
        pass
    log.debug("count = %d" % count)
    #download_many(jobs)
    pass
if __name__ == '__main__':
    parser = MyHTMLParser()
    parser.feed('<html><head><title>Test</title></head>'
                '<body><h1>Parse me!</h1></body></html>')
    download_files()

