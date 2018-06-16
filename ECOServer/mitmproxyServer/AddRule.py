from mitmproxy import http
import json
import redis
from datetime import datetime,timezone,timedelta
import time
import re
import urllib.parse
redisdb = "redisdb"
class RedisHelper():
    connection_pool = redis.ConnectionPool(host=redisdb, port=6379, db=0)
    strict_redis = redis.StrictRedis(connection_pool=connection_pool)

class AddRule:
    def __init__(self):
        rules_str = RedisHelper.strict_redis.get("rules").decode("utf-8")
        #rules_str = urllib.parse.unquote(rules_str)
        print(rules_str)
        self.rules = json.loads(rules_str)

        pass


    def now(self):
        dt = datetime.utcnow()
        # print(dt)
        dt = dt.replace(tzinfo=timezone.utc)
        # print(dt)
        tzutc_8 = timezone(timedelta(hours=0))
        local_dt = dt.astimezone(tzutc_8)
        # print(local_dt)
        return local_dt
        pass
    def match_url(self,tag,regex,flow:http.HTTPFlow):
        array = regex.findall(flow.request.url)
        if len(array)>0:
            print(flow.request.url)
            print("%s" % self.now().time())
            # print("postdata=%s"%flow.request.content.decode("utf-8"))
            # print(flow.request.method)
            # print("result=%s"%flow.response.content.decode("utf-8"))
            post_data = {}
            post_data["tag"] = tag
            post_data["url"] = flow.request.url
            post_data["data"] = flow.response.content.decode("utf-8")
            post_data["post"] = flow.request.content.decode("utf-8")
            post_data["time"] = time.mktime(self.now().timetuple())*1000
            json_str = json.dumps(post_data)
            print("json_str=%s" % json_str)
            RedisHelper.strict_redis.lpush("origin:" + tag, json_str)
            return True
        else:
            return False
        pass
    def response(self, flow:http.HTTPFlow):
        # print(flow.request.url)
        # p = re.compile(r"news.+?channel")
        # self.match_url("ydsdk", p, flow)
        for rule in self.rules :
            #print(rule["regStr"])
            p = re.compile(urllib.parse.unquote(rule["regStr"],"utf-8"), re.IGNORECASE)
            if self.match_url(rule["tag"],p,flow):
                break
            pass

        #flow.response.headers["count"] = str(self.num)


addons = [
    AddRule()
]


if __name__ == "__main__":
    p = re.compile(r'newsapi.sina.cn/\?resource=feed(.*)&channel=.*')
    url = "http://newsapi.sina.cn/?resource=feed&mpName=%E6%8E%A8%E8%8D%90&lDid=f122441e-3f26-4319-a092-a4340eb83589&oldChwm=12040_0006&upTimes=0&city=CHXX0138&loginType=0&authToken=9c531068929199eb9397d40b9114fca5&channel=news_toutiao&link=&authGuid=6408634870838567279&ua=Xiaomi-Redmi+5__sinanews__6.8.8__android__7.1.2&deviceId=615b25417ba9c49d&connectionType=2&resolution=720x1344&weiboUid=&mac=02%3A00%3A00%3A00%3A00%3A00&replacedFlag=1&osVersion=7.1.2&chwm=12040_0006&pullTimes=3&weiboSuid=&andId=5bb64be3f5ebeee8&from=6068895012&sn=a2ccc84b7ce5&behavior=manual&aId=01AiyEffHXZ2NNAiUOA2pJWrLwthIalVYKmjLPFK_gP5xeFl4.&localSign=a_65a9f111-e57e-45e0-97e6-507ad1d74ec9&deviceIdV1=615b25417ba9c49d&todayReqTime=0&osSdk=25&abver=1527850390688&listCount=29&accessToken=&downTimes=2&abt=314_302_297_281_275_269_267_255_253_251_249_241_237_231_229_228_226_217_215_207_203_191_189_187_185_153_149_143_141_135_128_113_111_106_65_57_45_37_21_18_16_13&lastTimestamp=1527942308&pullDirection=down&seId=fa20d53e22&imei=868238031871103&deviceModel=Xiaomi__Xiaomi__Redmi+5&location=30.581782%2C114.218291&authUid=0&loadingAdTimestamp=0&urlSign=694a2bff7f&rand=536"
    rel = p.findall(url)
    pass