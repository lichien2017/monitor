from mitmproxy import http
import json
import redis
from datetime import datetime,timezone,timedelta
import time
import re
import urllib

redisdb = "redisdb"
class RedisHelper():
    connection_pool = redis.ConnectionPool(host=redisdb, port=6379, db=0)
    strict_redis = redis.StrictRedis(connection_pool=connection_pool)

class AddRule:
    def __init__(self):
        rules_str = RedisHelper.strict_redis.get("rules")
        rules_str = urllib.parse.unquote(rules_str)
        print(rules_str)
        self.rules = json.loads(rules_str)

        pass


    def now(self):
        dt = datetime.utcnow()
        # print(dt)
        dt = dt.replace(tzinfo=timezone.utc)
        # print(dt)
        tzutc_8 = timezone(timedelta(hours=8))
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
            post_data["tag"] = ""
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
            p = re.compile(rule["regStr"], re.IGNORECASE)
            if self.match_url(rule["tag"],p,flow):
                break
            pass

        #flow.response.headers["count"] = str(self.num)


addons = [
    AddRule()
]


if __name__ == "__main__":
    p = re.compile(r'r.inews.qq.com/getQQNewsUnreadList.*')
    url = "https://r.inews.qq.com/getQQNewsUnreadList?last_id=20180528V12YJ200&forward=0&last_time=1527577220&lc_ids=&kankaninfo={%22refresh%22:0,%22gender%22:1,%22lastExp%22:8,%22scene%22:0}&newsTopPage=0&picType=&chlid=news_video_top&rendType=kankan&rtAd=1&user_chlid=news_news_19&page=3&channelPosition=1&Cookie=lskey%3D;skey%3D;uin%3D;%20luin%3D;logintype%3D0;%20main_login%3D;%20&uid=11ce66cea8677ae0&devid=11ce66cea8677ae0&appver=24_android_5.6.00&omgid=ac3fe75a887f634e7089ec5a4dff7018b0fb0010213310&qn-sig=54381a0e5f867e58977f8b80b80b9eb9&qn-rid=49e9a1ff-8319-4530-bd7f-461a8f4ba70e"
    rel = p.findall(url)
    pass