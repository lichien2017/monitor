from concurrent import futures
import requests
import os

from pymongo import MongoClient
from threading import Thread
import json
from util import *
import time
from analysis.rule_level0_service import RuleServiceLevel1
DEST_DIR = os.path.dirname(__file__) + "/files/"  # 服务启动后做映射过去
# log = SingleLogger().log

class MediaDownload(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._client = MongoClient(ConfigHelper.mongodbip, ConfigHelper.mongodbport)
        self._database = self._client["crawlnews"]
        self.thread_stop = False
        self.ruleServiceLevel1 = RuleServiceLevel1(ConfigHelper.load_rule_time)
        self.ruleServiceLevel1.load_rules(1)
        pass
    # 查询mongodb的资源详情
    def get_resource(self,res_msg):
        mongodb = self._client['crawlnews']
        rows = mongodb["originnews" + res_msg["time"]].find({"identity": res_msg["res_id"]})
        if rows == None or rows.count() == 0:
            return None
        return rows[0]
    # 检查要下载的文件是否存在数据库中，并且
    def check_download_url(self,url):
        mongodb = self._client['crawlnews']
        table = mongodb["download_url"]
        row = table.find_one({"url":Secret.md5(url)}) # 检查url是否存在，
        if row == None :
            return None
        return row["full_filename"]
        pass
    # 将新的下载文件路径写入数据库
    def write_download_url(self,url,full_filename):
        mongodb = self._client['crawlnews']
        table = mongodb["download_url"]
        #row = table.find_one({"url": Secret.md5(url)})  # 检查url是否存在，
        #这里应该做剔除重复判断，但是并行处理可能会有问题，所以不做剔除重复
        table.insert({"url": Secret.md5(url), "full_filename": full_filename})
        pass
    # 构造被下载文件的完整路径
    def get_full_filename(self,job):
        filename = Secret.md5(job["url"])
        path = os.path.join(DEST_DIR, job["dir"])  # 带上日期目录
        if not os.path.exists(path):
            os.makedirs(path)
        full_filename = os.path.join(DEST_DIR, job["dir"], filename)  # 拼接成完整路径
        return full_filename
        pass
    # 保存图片
    def save_media(self,media, full_filename):  # <5>
        # filename = Secret.md5(job["url"])
        # path = os.path.join(DEST_DIR, job["dir"]) # 带上日期目录
        # if not os.path.exists(path):
        #     os.makedirs(path)
        # full_filename = os.path.join(DEST_DIR, job["dir"], filename) #拼接成完整路径

        # full_filename = self.get_full_filename(job)
        with open(full_filename, 'wb') as fp:
            fp.write(media)

    def get_media(self,url):  # <6>
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:  # <1>
            resp.raise_for_status()  # 如果不是200 抛出异常
        return resp.content
    # 下载媒体，并保存
    def download_one(self,job):
        try:
            write = False
            url = job["url"]
            # 检查数据库是否有相同的下载路径
            result = self.check_download_url(url)
            if result == None:
                write = True # 表示新生成了一个文件路径
                full_filename = self.get_full_filename(job)
            else:
                full_filename = result
            if os.path.isfile(full_filename): #如果文件存在
                return url

            media = self.get_media(url)
        # 捕获 requests.exceptions.HTTPError
        except requests.exceptions.HTTPError as exc:  #
            # 如果有异常 直接抛出
            raise
        else:
            self.save_media(media, full_filename)
            # 将数据写入到数据库中
            if write: # 新建的路径才需要写入数据库
                self.write_download_url(url,full_filename)
        return url
    # 批量下载媒体文件
    def download_many(self,cc_list):
        # cc_list = cc_list[:5]
        # with futures.ProcessPoolExecutor() as executor:
        with futures.ThreadPoolExecutor(max_workers=20) as executor:
            to_do_map = {}
            for cc in cc_list:
                # if cc == None or cc == "" :
                #     continue
                future = executor.submit(self.download_one, cc)
                to_do_map[future] = cc
                msg = 'Scheduled for {}: {}'
                SingleLogger().log.debug(msg.format(cc, future))

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
                    SingleLogger().log.error('*** Error for {}: {}'.format(cc, error_msg))
                else:
                    msg = '{} result: {!r}'
                    SingleLogger().log.debug(msg.format(future, res))
                    results.append(res)

        return len(results)

    def run(self):
        while True:
            # 从消息队列中获取任务
            item = RedisHelper.strict_redis.rpop(ConfigHelper.download_msgqueue)
            if item != None:
                # {
                #     "res_id": "6564277366116319491",
                #     "time": "20180608"
                # }
                # log.debug(item.decode("utf-8"))
                res_msg = json.loads(item.decode("utf-8"))
                res = self.get_resource(res_msg) # 获取资源详情
                media = [] # 待下载资源队列
                if res != None:
                    if res["crawltimestr"] < "2018-06-08 15:50:28":
                        continue
                    # 读取资源中的图片
                    logos = []
                    if res["logo"].find("、")>=0 :
                        logos = res["logo"].split("、")
                    else:
                        logos = res["logo"].split(",")

                    gallary=[]
                    if res["gallary"].find("、") >= 0:
                        gallary = res["gallary"].split("、")
                    else:
                        gallary = res["gallary"].split(",")

                    if "video" in res: # 如果有视频
                        media = media + res["video"].split(",")
                        pass
                    media = media + logos + gallary
                    media = [x for x in media if x != '' and (x.startswith("http://") or x.startswith("https://"))]
                    identity = res["identity"]

                    dir_name = res_msg["time"]  # + "/" + res_msg["res_id"]
                    jobs = []
                    for img in media:
                        jobs.append({"url": img, "dir": dir_name, "res_id": res_msg["res_id"]})
                    result = self.download_many(jobs)
                    SingleLogger().log.debug("result=%d" % result)
                    # 下载完成后发送到指定队列
                    SingleLogger().log.debug("Rule1server.add_resource_to_all_queue == %s", json.dumps(res_msg))
                    self.ruleServiceLevel1.add_resource_to_all_queue(json.dumps(res_msg))
            time.sleep(2)
    pass