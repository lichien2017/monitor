
from screencap.screencap_match_recv import ScreenCaptureMatchRecv
from screencap.screencap_match_senddata import ScreenCaptureMatchSendData
from concurrent import futures
import requests
import os
from util import *
import  sys
import json
import multiprocessing
import time
#
# def worker(interval):
#     while True:
#         # 不同规则从缓存中获取资源id进行处理
#         item = RedisHelper.strict_redis.rpop("video:process")
#         if item != None:
#             SingleLogger().log.debug(item)  # msg = {"res_id":resource_id,"time":LocalTime.now_str()}
#             # res_id = item.decode("utf-8")
#             res_msg = json.loads(item)
#             sub_job = res_msg["id"] #""sendjob:%s:%s" % (self.__class__.__name__, res_recv[0])  # 子任务消息key
#             RedisHelper.strict_redis.hset(sub_job, res_msg["seq"],0) # 临时设置为0
#             #SingleLogger().log.debug("%s 获取到数据:%s" % (self.__class__.__name__, res_msg["res_id"]))
#             RedisHelper.strict_redis.lpush(res_msg["resp"],res_msg["resdata"])
#         else:
#             time.sleep(1)
#
# if __name__ == "__main__":
#     p = multiprocessing.Process(target = worker, args = (3,))
#     p.daemon = True
#     p.start()
#     p.join()  # 加入join方法



# def main():
#     r = ScreenCaptureMatch()
#     r.start()
#     pass

if __name__ == "__main__" :
    SingleLogger().log.debug("测试")
    # main()
    recv = ScreenCaptureMatchRecv()
    send = ScreenCaptureMatchSendData()
    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        to_do_map = {}

        future = executor.submit(recv.start)
        to_do_map[future] = "ScreenCaptureMatchRecv"
        future = executor.submit(send.start)
        to_do_map[future] = "ScreenCaptureMatchSendData"
        # msg = 'Scheduled for {}: {}'
        # SingleLogger().log.debug(msg.format(cc, future))
        #
        # for cc in cc_list:
        #     # if cc == None or cc == "" :
        #     #     continue
        #     future = executor.submit(self.download_one, cc)
        #     to_do_map[future] = cc
        #     msg = 'Scheduled for {}: {}'
        #     SingleLogger().log.debug(msg.format(cc, future))

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
        count = len(results)
    pass