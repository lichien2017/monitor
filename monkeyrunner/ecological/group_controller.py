"""
deivice group 的控制类
"""
import device
import redis
import configparser
import json

class DeviceGroupController:
    _msg_channel = None
    _groups = []
    _redis_server = None

    def __init__(self,channel="groupchannel"):
        self._msg_channel = channel #可以指定消息频道
        config = configparser.ConfigParser()
        config.read("config.ini")
        pool = redis.ConnectionPool(host=config.get("global", "redisip"), port=6379, db=config.get("global", "redisdb"))
        _redis_server = redis.StrictRedis(connection_pool=pool)

    def start(self):
        print('DeviceGroupController start')
        self._redis_subscript()

    def _redis_subscript(self):
        p = self._redis_server.pubsub()
        p.subscribe(self._msg_channel)  # 控制器的消息队列
        for item in p.listen():
            print(item)
            if item['type'] == 'message':
                data = item['data']
                result = self._parse_redis_message(data)  # 解析数据包
                if result == False:
                    break;
            elif item['type'] == 'subscribe': #开始监听消息队列了
                self._get_default_settings()   #获取最新的配置，配置中包含需要启动的设备数，以及设备中runner的个数
        p.unsubscribe('spub')

    def _get_default_settings(self):
        data = self._redis_server.get(self._msg_channel) #这里获取最新的配置信息
        if(data != None):
            print("get_default_settings 获取到的默认配置:"+data.decode("utf-8"))
            settings = json.loads(data.decode("utf-8"))
            self._start_all_group_thread(settings)
        else:
            print("获取到的默认配置失败，等待控制信号")


    def _parse_redis_message(self,msg):#数据解包，需要多少runner工作，每个runner的消息对队列标示
        print("main_parse_redis_message")
        data = json.loads(msg.decode("utf-8")) #消息数据部分
        print(data)
        if data['type'] == 'START':  # 启动
            sub_data = data['data']
            self._start_all_group_thread(sub_data)  # 解析数据包
        elif data['type'] == 'RESTART':  # 重新启动
            self._close_all_group()
            sub_data = data['data']
            self._start_all_group_thread(sub_data)  # 解析数据包
        elif data['type'] == 'STOP':  # 结束了就退出吧
            self._close_all_group()
            return False
        return True


    def _start_all_group_thread(self,settings):#数据解包，需要多少runner工作，每个runner的消息对队列标示
        print("_start_all_group_thread")
        if settings == None:
            return
        self._groups[:] = []   #清空数据
        for item in settings:
            deviceid = item["deviceid"]
            group = device.DeviceGroup(deviceid,item["runner"])
            self._groups.append(group)
            group.start()

    def _close_all_group(self):
        for g in self._groups:
            g.stop()

