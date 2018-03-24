"""
设备分组，每个设备按跑的多少个应用进行分组，每个设备都有唯一标示
标示可以通过 adb devices获取到
"""
import redis
import configparser
import json
import time
from threading import Thread
from device.runner import DeviceRunner

class DeviceGroup(Thread):
    _device_id = ""                                            #设备的唯一标示
    _repeat_time = 5
    _msg_channel = ""                                   #监听消息队列的渠道id
    # _runners = []                                       #monkeyrunner列表
    _runner_settings = []                               #每个runner的配置
    def __init__(self,device_id,repeat_time,settings):           #每一个分组对应一台手机设备，每个设备都有一个唯一标示
        Thread.__init__(self)
        self.interval = 1
        self.thread_stop = False
        self._device_id = device_id
        self._repeat_time = repeat_time
        self._runner_settings = settings

    def run(self):  # Overwrite run() method, put what you want the thread do here
        if (self._runner_settings!=None):   #如果配置信息不为空时，直接启动相关线程，否则监听消息端口等待命令
            while not self.thread_stop :
                print("DeviceID(%s) is running" % self._device_id)
                self._msg_channel = "%s:%s" % ('groupchannel', self._device_id)  # 当前分组的控制消息队列
                for runner in self._runner_settings:
                    r = DeviceRunner(runner)   #实例化一个runner
                    # self._runners.append(r)    #加入runner数组,不需要管理，顺着执行
                    r.run()                    #奔跑吧，兄弟 -_-!!
                    self._waitting(self._repeat_time)  # 重启脚本时间间隔
        print("DeviceID(%s) is stop" % self._device_id)
        # else:
        #     self._redis_subscript()            #阻塞主线程，等待控制命令
        # print('end device_group')

    def stop(self):
        self.thread_stop = True

    def _waitting(self, second):
        # 等待時間
        time.sleep(second)
    # def _redis_subscript(self):
    #     config = configparser.ConfigParser()
    #     config.read("config.ini")
    #     redisip = config.get("global","redisip")
    #     pool = redis.ConnectionPool(host=redisip, port=6379, db=config.get("global", "redisdb"))
    #     r = redis.StrictRedis(connection_pool=pool)
    #     p = r.pubsub()
    #     p.subscribe(self._msg_channel) #分组的消息
    #     for item in p.listen():
    #         print(item)
    #         if item['type'] == 'message': #启动
    #             data = item['data']
    #             result = self.parse_redis_message(data) #解析数据包
    #             if result == False:
    #                 break;
    #     p.unsubscribe('spub')
    #
    # def parse_redis_message(self,msg):#数据解包，需要多少runner工作，每个runner的消息对队列标示
    #     print("parse_redis_message")
    #     data = json.loads(msg.decode("utf-8")) #消息数据部分
    #     print(data)
    #     if data['type'] == 'START':  # 启动
    #         sub_data = data['data']
    #         self.parse_submessage(sub_data)  # 解析数据包
    #     elif data['type'] == 'RESTART':  # 重新启动
    #         self._close_all_runner()
    #         sub_data = data['data']
    #         self.parse_submessage(sub_data)  # 解析数据包
    #     elif data['type'] == 'PRINT':
    #         self._print_all_runner() #打印当前所有runner的状态
    #     elif data['type'] == 'STOP':  # 结束了就退出吧
    #         self._close_all_runner()
    #         return False
    #     return True
    #
    # def parse_submessage(self,runner_settings):#数据解包，需要多少runner工作，每个runner的消息对队列标示
    #     print("parse_submessage")
    #     if runner_settings == None:
    #         return
    #     self._runners[:]  = []
    #     for runner in runner_settings:
    #         r = DeviceRunner(runner)
    #         self._runners.append(r)
    #         r.start()
    #
    # def to_string(self):
    #     print('当前有%s脚本正在运行,详情如下：\n' % (self._runners.count()))
    #     self._print_all_runner()
    #
    # def _print_all_runner(self):
    #     for r in self._runners:
    #         r.to_string()
    #
    # def _close_all_runner(self):
    #     for r in self._runners:
    #         r.stop()
    #     self._runners[:] = []
