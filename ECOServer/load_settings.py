from threading import Thread
import pymysql
from util import *
import redis
import json


class Setting(Thread):

    def applist(self,cursor):
        # 使用execute方法执行SQL语句
        cursor.execute("SELECT * FROM app_information  WHERE isonline = 1")
        # 使用 fetchone() 方法获取一条数据
        data = cursor.fetchall()
        if bool(data) != True:
            print("( ⊙ o ⊙ )啊哦，applist竟然没有查询到数据结果")
        else:
            # 对查询出的数据进行处理
            appv = "";
            for record in data:
                v = "{'pkg':'%s','tag':'%s'}" % (
                    record[2], record[0])
                appv += v + ","
            value = json.dumps(appv[:-1], ensure_ascii=False)
            value = value.replace("\"", "")
            value = value.replace("\'", "\"")
            self.redis.set('applist', "[" + value + "]")

    def rules(self, cursor):
        # 使用execute方法执行SQL语句
        cursor.execute("SELECT * FROM proxy_rules  WHERE isonline = 1")
        # 使用 fetchone() 方法获取一条数据
        rulesdata = cursor.fetchall()
        if bool(rulesdata) != True:
            print("( ⊙ o ⊙ )啊哦，rules竟然没有查询到数据结果")
        else:
            # 对查询出的数据进行处理
            rulesv = "";
            for record in rulesdata:
                v = "{'tag':'%s','regStr':'%s'}" % (
                    record[1], record[2])
                rulesv += v + ","
            value = json.dumps(rulesv[:-1], ensure_ascii=False)
            value = value.replace("\"", "")
            value = value.replace("\'", "\"")
            self.redis.set('rules', "[" + value + "]")

    def groupchannel(self, cursor):
        #  使用execute方法执行SQL语句
        cursor.execute("SELECT * FROM v_deviceinformation WHERE isonline=1")
        # 使用 fetchone() 方法获
        # 取一条数据
        phonedata = cursor.fetchall()
        if bool(phonedata) != True:
            print("( ⊙ o ⊙ )啊哦，phone竟然没有查询到数据结果")
        else:
            # 对查询出的数据进行处理
            group = "";
            for record in phonedata:
                repeat_time = record[7]
                phonenum = record[0]
                sql = "SELECT * FROM crawl_runner WHERE device_serialnum='" + phonenum + "' AND isonline =1"
                cursor.execute(sql)
                # 使用 fetchone() 方法获取一条数据
                rundata = cursor.fetchall()
                if bool(rundata) != True:
                    print("( ⊙ o ⊙ )啊哦，phone竟然没有查询到数据结果")
                else:
                    runv = ""
                    for record in rundata:
                        appsql = "SELECT * FROM app_information WHERE tag = '"+record[1] +"'AND isonline = 1"
                        cursor.execute(appsql)
                        # 使用 fetchone() 方法获取一条数据
                        appdata = cursor.fetchall()
                        if bool(appdata) != True:
                            print("( ⊙ o ⊙ )啊哦，App下线了？")
                            return
                        referencesql ="SELECT * FROM app_category WHERE app_tag= '"+record[1]+"' AND tag='"+record[13]+"' AND isonline=1"
                        cursor.execute(referencesql)
                        # 使用 fetchone() 方法获取一条数据
                        referencedata = cursor.fetchall()
                        if bool(referencedata) != True:
                            print("( ⊙ o ⊙ )啊哦，App栏目下线了？")
                            return
                        dict = {'activity':record[2],'categroy':record[3],'clickpoint':record[5],'endpoint': record[8],
                                'headscreencount':record[14],'imgserver':record[10],'imp_class':record[12],
                                'imp_module':record[11],'reference':record[13],'setuptime':record[4],
                                'sleeptime':record[6],'speed':record[9],'startpoint':record[7],'tag':record[1]}
                        runv += str(dict) + ","
                    value = json.dumps(runv[:-1], ensure_ascii=False)
                    value = "'deviceid': '%s'," % phonenum + "'repeattime':'%s'," % repeat_time \
                            + "'runner': [" + value.replace("\"", "") + "]"
                    value = "{" + value.replace("\'", "\"") + "}"
                    group += value + ","
            group = group.replace("\"repeattime\":\"", "\"repeattime\":")
            group = group.replace("\",\"runner\":", ",\"runner\":")
            self.redis.set('groupchannel', "[" + group[:-1] + "]")

    def training_models(self, cursor):
        cursor.execute("SELECT * FROM training_models WHERE isdefault=0")
        # 使用 fetchone() 方法获取一条数据
        modelsdata = cursor.fetchall()
        if bool(modelsdata) != True:
            print("( ⊙ o ⊙ )啊哦，竟然没有查询到数据结果")
        else:
            # 对查询出的数据进行处理
            for record in modelsdata:
                self.redis.set("default_model:%s:%s" % (record[3], record[4]), record[2])


    def run(self):
        self.sdb = pymysql.connect(ConfigHelper.mysql_ip, ConfigHelper.mysql_user,
                                   ConfigHelper.mysql_pwd, ConfigHelper.mysql_db, charset='utf8')
        self.redis = redis.Redis(host=ConfigHelper.redisip, port=ConfigHelper.redisport, db=ConfigHelper.redisdb)
        # mysql使用cursor()方法获取操作游标
        cursor = self.sdb.cursor()
        self.applist(cursor)
        self.rules(cursor)
        self.groupchannel(cursor)
        self.training_models(cursor)


if __name__ == '__main__':
    Setting().run()
    pass







