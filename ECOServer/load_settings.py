from threading import Thread
import pymysql
from util import *
import redis
import json


class Setting(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.sdb = pymysql.connect(ConfigHelper.mysql_ip, ConfigHelper.mysql_user,
                                  ConfigHelper.mysql_pwd, ConfigHelper.mysql_db, charset='utf8')
        self.redis = redis.Redis(host=ConfigHelper.redisip, port=ConfigHelper.redisport, db=ConfigHelper.redisdb)

    def run(self):
        # mysql使用cursor()方法获取操作游标
        cursor = self.sdb.cursor()
        # applist
        # 使用execute方法执行SQL语句
        cursor.execute("SELECT * FROM app_information  WHERE isonline = 1")
        # 使用 fetchone() 方法获取一条数据
        data = cursor.fetchall()
        if bool(data) != True:
            print("( ⊙ o ⊙ )啊哦，applist竟然没有查询到数据结果")
        else:
            # 对查询出的数据进行处理
            self.i = 0;
            appv ="";
            for record in data:
                row = data[self.i]
                v = "{'pkg':'%s','tag':'%s'}" % (
                row[2], row[0])
                appv += v +","
                self.i += 1
            value = json.dumps(appv[:-1], ensure_ascii=False)
            value = value.replace("\"","")
            value = value.replace("\'", "\"")
            self.redis.set('applist',"["+value+"]")

        # rules
        # 使用execute方法执行SQL语句
        cursor.execute("SELECT * FROM proxy_rules  WHERE isonline = 1")
        # 使用 fetchone() 方法获取一条数据
        rulesdata = cursor.fetchall()
        if bool(rulesdata) != True:
            print("( ⊙ o ⊙ )啊哦，rules竟然没有查询到数据结果")
        else:
            # 对查询出的数据进行处理
            self.r = 0;
            rulesv = "";
            for record in rulesdata:
                row = rulesdata[self.r]
                v = "{'pkg':'%s','regStr':'%s'}" % (
                    row[1], row[2])
                rulesv += v + ","
                self.r += 1
            value = json.dumps(rulesv[:-1], ensure_ascii=False)
            value = value.replace("\"", "")
            value = value.replace("\'", "\"")
            self.redis.set('rules', "[" + value + "]")


        # groupchannel
        # 使用execute方法执行SQL语句
        cursor.execute("SELECT * FROM crawl_rules")
        # 使用 fetchone() 方法获取一条数据
        phonedata = cursor.fetchall()
        if bool(phonedata) != True:
            print("( ⊙ o ⊙ )啊哦，phone竟然没有查询到数据结果")
        else:
            # 对查询出的数据进行处理
            self.p = 0;
            group ="";
            for record in phonedata:
                row = phonedata[self.p]
                repeat_time =row[1]
                phonenum =row[0]
                sql = "SELECT * FROM crawl_runner WHERE device_serialnum='"+phonenum+"' AND isonline =1";
                print(sql)
                cursor.execute(sql)
                # 使用 fetchone() 方法获取一条数据
                rundata = cursor.fetchall()
                if bool(rundata) != True:
                    print("( ⊙ o ⊙ )啊哦，phone竟然没有查询到数据结果")
                else:
                    self.runner = 0;
                    runv=""
                    for record in rundata:
                        row = rundata[self.runner]
                        v = "{'activity':'%s','categroy':'%s','clickpoint':'%s','endpoint':'%s','headscreencount':'%s','imgserver':'%s'," \
                            "'imp_class':'%s','imp_module':'%s','reference':'%s','setuptime':'%s','sleeptime':'%s'" \
                            ",'speed':'%s','startpoint':'%s','tag':'%s'}" % (
                            row[2], row[3],row[5],row[8],row[14],row[10],row[12],row[11],row[13],row[4],row[6],row[9],row[7],row[1])
                        runv += v + ","
                        self.runner += 1
                    value = json.dumps(runv[:-1], ensure_ascii=False)
                    value = "'deviceid': '%s'," % phonenum+"'repeattime': '%s'," % repeat_time\
                            + "'runner': [" + value.replace("\"", "")+"]"
                    value =  "{" + value.replace("\'", "\"") +"}"
                    group += value + ","
                self.p += 1
            self.redis.set('groupchannel', "[" + group[:-1] + "]")

        # training_models
        cursor.execute("SELECT * FROM training_models WHERE isdefault=0")
        # 使用 fetchone() 方法获取一条数据
        modelsdata = cursor.fetchall()
        if bool(modelsdata) != True:
            print("( ⊙ o ⊙ )啊哦，竟然没有查询到数据结果")
        else:
            # 对查询出的数据进行处理
            self.m = 0;
            modelsv ="";
            for record in modelsdata:
                row = modelsdata[self.m]
                self.redis.set("default_model:%s:%s"% (row[3],row[4]),row[2])
                self.m += 1

if __name__ == '__main__':
    seting = Setting()
    seting.run()
    pass







