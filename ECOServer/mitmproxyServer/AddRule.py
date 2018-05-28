from mitmproxy import ctx
from mitmproxy import http
import json
import redis
from datetime import datetime,timezone,timedelta
import time
import re

class RedisHelper():
    connection_pool = redis.ConnectionPool(host="redisdb", port=6379, db=0)
    strict_redis = redis.StrictRedis(connection_pool=connection_pool)

class AddRule:
    def __init__(self):
        self.p = re.compile(r'.+?-channel', re.IGNORECASE)
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
    def response(self, flow:http.HTTPFlow):
        #print(flow.request.url)
        if self.p.match(flow.request.url):
            print(flow.request.url)
            print("%s" % self.now().time())
            # print("postdata=%s"%flow.request.content.decode("utf-8"))
            # print(flow.request.method)
            # print("result=%s"%flow.response.content.decode("utf-8"))
            post_data = {}
            post_data["tag"] = ""
            post_data["url"] = flow.request.url
            post_data["str"] = flow.response.content.decode("utf-8")
            post_data["post"] = flow.request.content.decode("utf-8")
            post_data["time"] = time.mktime(self.now().timetuple())
            json_str = json.dumps(post_data)
            print("json_str=%s" % json_str)
            RedisHelper.strict_redis.lpush("origin:yiidan", json_str)
        #flow.response.headers["count"] = str(self.num)


addons = [
    AddRule()
]


if __name__ == "__main__":
    p = re.compile(r'.+?-channel', re.IGNORECASE)
    url = "https://124.243.231.139/Website//channel/news-list-for-hot-channel?searchentry=channel_navibar&reqid=b6fcpe5d_1527486704709_344033&eventid=6759219382e0a6acd-5a73-46b3-b754-49907be92c94&infinite=true&distribution=app.qq.com&refresh=1&appid=yidian&cstart=0&platform=1&cv=4.6.0.5&fields=docid&fields=date&fields=image&fields=image_urls&fields=like&fields=source&fields=title&fields=url&fields=comment_count&fields=up&fields=down&cend=30&version=020600&ad_version=010946&group_fromid=g181&collection_num=0&net=wifi"
    rel = p.match(url)
    pass