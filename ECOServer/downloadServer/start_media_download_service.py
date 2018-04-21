
from concurrent import futures
import requests
import os
import hashlib
import pymongo
import redis
import time
from config import ConfigHelper
from log import Logger
import json
log = Logger()
# 设定ThreadPoolExecutor 类最多使用几个线程
MAX_WORKERS = 20
# 图片保存地址
DEST_DIR = os.path.dirname(__file__) + "/files/"  # "/mnt/download_media/"
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
def save_image(img, filename):  # <5>
    path = os.path.join(DEST_DIR, filename)
    with open(path, 'wb') as fp:
        fp.write(img)



def get_image(url):  # <6>
    resp = requests.get(url)
    if resp.status_code != 200:  # <1>
        resp.raise_for_status() # 如果不是200 抛出异常
    return resp.content

def download_one(url):
    try:
        image = get_image(url)
    # 捕获 requests.exceptions.HTTPError
    except requests.exceptions.HTTPError as exc:  #
        # 如果有异常 直接抛出
        raise
    else:
        save_image(image, get_md5(url))
    return url



def download_many(cc_list):
    # cc_list = cc_list[:5]
    # with futures.ProcessPoolExecutor() as executor:
    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        to_do_map = {}
        for cc in sorted(cc_list):
            # if cc == None or cc == "" :
            #     continue
            future = executor.submit(download_one, cc)
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

def get_resource(res_msg):
    mongodb = mongodb_client['crawlnews']
    rows = mongodb["originnews"+res_msg["time"]].find({"identity":res_msg["res_id"]})
    if rows == None or rows.count() == 0:
        return None
    # print(rows)
    return rows[0]



if __name__ == '__main__':
    while True :
        item = redis_server.rpop(ConfigHelper.download_msgqueue)
        if item != None :
           log.debug(item.decode("utf-8"))
           res_msg = json.loads(item.decode("utf-8"))
           res = get_resource(res_msg)
           images = []
           if res !=None :
               # 读取资源中的图片
               logos = res["logo"].split(",")
               gallary = res["gallary"].split(",")
               images = logos + gallary
               images = [x for x in images if x != '' and (x.startswith("http://") or x.startswith("https://"))]
               download_many(images)
        time.sleep(2)

