
from pymongo import MongoClient
from threading import Thread
import pymysql
from util import *
from mysqldb.mysql_helper import MySQLHelper
import datetime


class Collector(Thread):
    # 不必要获前一天的数据，改为获取当天每小时同步
    time_go = 0
    def __init__(self,time_go=0):
        Thread.__init__(self)
        self.time_go = 0
        self._client = MongoClient(ConfigHelper.mongodbip, ConfigHelper.mongodbport)
        self._database = self._client["crawlnews"]
        self.thread_stop = False
        pass
    # 处理单列的有害数据
    # def copy_data_one_column(self,table_name,rule_tag,date):
    #     if table_name == None:
    #         SingleLogger().log.debug("table_name is None")
    #         return
    #     table = self._database[table_name]
    #     rows = table.find() # 查询出所有数据
    #     conn = MySQLHelper.pool_connection.get_connection()
    #     # 创建游标
    #     cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    #     for row in rows :
    #         res = self.get_resource(date, row["res_id"])
    #         if res == None:
    #             SingleLogger().log.error("resid = %s,没有找到详情信息，所以跳过"% row["res_id"])
    #             continue
    #         # insert_sql =
    #         # 执行SQL，并返回收影响行数
    #         try:
    #             row_count = cursor.execute("""insert into `analysis_data_total`(`res_id`,`create_date`,`rule_tag`,`app_tag`,
    #                             `category_tag`,`deleted`,`title`,`description`,`shorturl`,`changed`,`crawl_time`)
    #                             VALUES('%s','%s','%s','%s','%s',0,'%s','%s','%s',0,'%s')  ON DUPLICATE Key UPDATE res_id = '%s'
    #                          """ % (row["res_id"],date,rule_tag,res["app_tag"],res["category_tag"],pymysql.escape_string(res["title"]),
    #                                 pymysql.escape_string(res["description"]),res["shorturl"],res["crawltimestr"],row["res_id"]))
    #             conn.commit()
    #             SingleLogger().log.debug(row)
    #         except Exception as e:
    #             SingleLogger().log.error(e)
    #         pass
    #     cursor.close()
    #     conn.close()
    #     pass
    # 汇总数据将违规项分列进行
    def copy_data_to_total(self,table_name,rule_tag,date):
        if table_name == None:
            SingleLogger().log.debug("table_name is None")
            return
        table = self._database[table_name]

        yestoday_time = LocalTime.nowtime_str(-1).strftime("%Y-%m-%d %H:%M:%S")
        yestoday_nowtime = LocalTime.from_today(self.time_go).strftime("%Y-%m-%d %H:%M:%S")
        SingleLogger().log.debug("======yestoday_time=======>%s" % yestoday_time)
        SingleLogger().log.debug("======yestoday_nowtime=======>%s" % yestoday_nowtime)

        rows = table.find({'record_time': {'$gte': yestoday_time, '$lte': yestoday_nowtime}})
        
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        for row in rows :
            res = self.get_resource(date, row["res_id"])
            if res == None or self.checkInTags(res["app_tag"]):
                SingleLogger().log.error("resid = %s,没有找到详情信息，所以跳过"% row["res_id"])
                continue
            # insert_sql =
            # 执行SQL，并返回收影响行数
            try:

                #result = cursor.fetchone()

                row_count = cursor.execute("""select res_id from analysis_data_normal_total 
                                  where res_id = '%s' and create_date = '%s'""" % (row["res_id"],date))
                if row_count == 0 :#插入新的数据
                    screenshot = ""
                    screen_index = -1
                    if res["restype"] == 4 :
                        screenshot = res["gallary"]
                        screen_index = 1
                    sql_str = """INSERT ignore INTO `analysis_data_normal_total`
                                    (`res_id`,
                                    `title`,
                                    `description`,
                                    `crawl_time`,
                                    `XueXingBaoLiRule`,
                                    `screenshot`,
                                    `screen_index`,
                                    `app_tag`,
                                    `category_tag`,
                                    `shorturl`,
                                    `create_date`,
                                    `SexyRule`,
                                    `PoliticalRule`,
                                    `ZongJiaoRule`,
                                    `BiaoTiDangRule`,top_news,ad_news,hot_news,topic_news,we_media,source,contents,res_type)
                                    VALUES
                                    ('%s','%s','%s','%s',%d,'%s',%d,'%s','%s','%s','%s',%d,%d,%d,%d,%d,%d,%d,%d,%d,'%s','%s',%d)
                                    """ % (
                                    row["res_id"],pymysql.escape_string(res["title"]),pymysql.escape_string(res["description"]),res["crawltimestr"],0,screenshot,screen_index,
                                    res["app_tag"], res["category_tag"], res["shorturl"],date, 0,0,0,0, 0,0,0,0,0,res["source"],res["content"],res["restype"])

                    SingleLogger().log.debug(sql_str)
                    row_count = cursor.execute(sql_str)
                    #将数据插入到指定的处理消息队列(id，日期)
                    RedisHelper.strict_redis.lpush("newslist",row["res_id"]+","+date)
                    pass
                # 更新相对应的规则字段
                row_count = cursor.execute("""update analysis_data_normal_total 
                                                                  set `%s` = 1 where res_id = '%s' and create_date = '%s'"""
                                           % (rule_tag, row["res_id"], date))

                conn.commit()
                SingleLogger().log.debug(row)
            except Exception as e:
                SingleLogger().log.error(e)
            pass
        cursor.close()
        conn.close()
        pass
    #得到资源详情数据
    def get_resource(self,date,res_id):
        res_table = self._database["originnews%s" % date]
        res = res_table.find_one({"identity": res_id})
        return res
        pass
    # 处理ORC的数据，识别资源是第几屏幕
    # def copy_data_screen_orc(self,table_name,rule_tag,date):
    #     if table_name == None:
    #         SingleLogger().log.debug("table_name is None")
    #         return
    #
    #     table = self._database[table_name]
    #     rows = table.find()
    #     conn = MySQLHelper.pool_connection.get_connection()
    #     # 创建游标
    #     cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    #     for row in rows:
    #         if row["screen_index"] !=-1:
    #             res = self.get_resource(date,row["res_id"])
    #             if res == None :
    #                 continue
    #             try:
    #                 row_count = cursor.execute("""insert into `analysis_data_total`(`res_id`,`create_date`,`rule_tag`,`screenshot`,
    #                                   `screen_index`,
    #                                   `app_tag`,`category_tag`,`deleted`,`title`,`description`,`shorturl`,`changed`,`crawl_time`)
    #                                         VALUES('%s','%s','%s','%s','%s','%s','%s',0,'%s','%s','%s',0,'%s')
    #                                         ON DUPLICATE Key UPDATE res_id = '%s'
    #                                      """ % (row["res_id"], date, rule_tag, row["image"],row["screen_index"],
    #                                             res["app_tag"],res["category_tag"],pymysql.escape_string(res["title"]),pymysql.escape_string(res["description"]),
    #                                             res["shorturl"],res["crawltimestr"],row["res_id"]))
    #                 conn.commit()
    #             except Exception as e:
    #                 SingleLogger().log.error(e)
    #         SingleLogger().log.debug(row)
    #         pass
    #     cursor.close()
    #     conn.close()
    #     pass
    # ocr在总表中匹配图片
    def copy_data_to_total_screen_orc(self,table_name,rule_tag,date):
        if table_name == None:
            SingleLogger().log.debug("table_name is None")
            return

        table = self._database[table_name]
        rows = table.find()
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        for row in rows:
            if row["screen_index"] !=-1:
                res = self.get_resource(date,row["res_id"])
                if res == None or self.checkInTags(res["app_tag"]):
                    continue
                try:
                    row_count = cursor.execute("""select res_id 
                                                  from analysis_data_normal_total 
                                                  where res_id = '%s' and create_date = '%s'""" % (row["res_id"], date))
                    if row_count == 0:  # 插入新的数据
                        sql_str = """INSERT ignore INTO `analysis_data_normal_total`
                                                        (`res_id`,
                                                        `title`,
                                                        `description`,
                                                        `crawl_time`,
                                                        `XueXingBaoLiRule`,
                                                        `screenshot`,
                                                        `screen_index`,
                                                        `app_tag`,
                                                        `category_tag`,
                                                        `shorturl`,
                                                        `create_date`,
                                                        `SexyRule`,
                                                        `PoliticalRule`,
                                                        `ZongJiaoRule`,
                                                        `BiaoTiDangRule`)
                                                        VALUES
                                                        ('%s','%s','%s','%s',%d,'%s',%s,'%s','%s','%s','%s',%d,%d,%d,%d)
                                                        """ % (
                            row["res_id"], pymysql.escape_string(res["title"]), pymysql.escape_string(res["description"]),
                            res["crawltimestr"], 0, row["image"],row["screen_index"],
                            res["app_tag"], res["category_tag"], res["shorturl"], date, 0, 0, 0, 0)

                        SingleLogger().log.debug(sql_str)
                        row_count = cursor.execute(sql_str)
                        pass
                    # 更新
                    row_count = cursor.execute("""update analysis_data_normal_total 
                                                  set screenshot = '%s' ,screen_index = %s 
                                                  where res_id = '%s' and create_date = '%s'"""
                                               % (row["image"],row["screen_index"], row["res_id"], date))

                    conn.commit()
                except Exception as e:
                    SingleLogger().log.error(e)
            SingleLogger().log.debug(row)
            pass
        cursor.close()
        conn.close()
        pass
    #移除老的数据
    def remove_all_table_data(self,date):
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # 执行SQL，并返回收影响行数
        row_count = cursor.execute("""
                        delete from `analysis_data_normal_total`
                        where create_date = '%s'
                        """ % (date))
        cursor.close()
        conn.close()
        pass
    # 移除掉空的数据
    def remove_all_empty_data(self,date):
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        sql = """delete from `analysis_data_normal_total`
                            where (`BiaoTiDangRule`+`PoliticalRule`+`SexyRule`+`XueXingBaoLiRule`+`ZongJiaoRule`
                            +top_news+ad_news+hot_news+topic_news+we_media)=0 and create_date = '%s'
                            and status =0 and app_tag not in (select tag from `app_information` where `isartificial`=1)
                                """ % (date)
        SingleLogger().log.debug(sql)
        row_count = cursor.execute(sql)

        cursor.close()
        conn.close()
        pass
    # 统计指定时间的数据
    def total_count(self,date):
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # 总涉嫌违规条数
        row_count = cursor.execute("""
        select count(distinct res_id) as ct from `analysis_data_normal_total`
where create_date = '%s'
        """% (date))
        result = cursor.fetchone()
        bad_count = result["ct"]
        # 总条数
        table = self._database["originnews" + date]
        count = table.count()
        # 执行SQL，并返回收影响行数
        row_count = cursor.execute("""
        insert into `analysis_collectCount`(`create_date`,`bad_count`,`count`)
        values('%s',%d,%d) ON DUPLICATE KEY UPDATE bad_count = %d,count= %d
        """ % (date,bad_count,count,bad_count,count))

        cursor.close()
        conn.close()
        pass

    # 查询人工审核的应用tag
    def queryManualApp(self):
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        row_count = cursor.execute("select tag from app_information where isartificial = 1")
        result = cursor.fetchone()
        tags = []
        while result != None:
            tags.append(result)
            result = cursor.fetchone()
            pass
        return tags
        pass

    # 检查是否是人工审核的应用
    def checkInTags(self,tag):
        for tmp in self.tags :
            if tmp == tag :
                return True
        return False
        pass
    # 导入机器审核的数据，不包括人工审核数据
    def batchImportMachineData(self):
        # 先找到有哪些表需要归档的，可以从规则表找
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

        # 执行SQL，并返回收影响行数 select * from analysis_rules where level = 1 and isonline = 1
        row_count = cursor.execute("select * from analysis_rules where isonline = 1")
        # 获取所有数据
        result = cursor.fetchone()
        yestoday = LocalTime.from_today(self.time_go)
        yestoday_str = yestoday.strftime("%Y%m%d")
        # 这里修改了一下，对于重复的数据插入进行了调整，不会报错也不会有重复数据，所以放心插入吧
        #self.remove_all_table_data(yestoday_str)  # 清除某一天数据
        #
        while result != None:
            SingleLogger().log.debug(result)
            table_name = "%s%s" % (result["mongodb_tablename"], yestoday_str)
            SingleLogger().log.debug("table_name is %s", table_name)

            if result["mongodb_tablename"].startswith("screencapocr"):  # 如果是判断第几屏幕，单独处理
                # self.copy_data_screen_orc(table_name,result["mongodb_tablename"],yestoday_str)

                self.copy_data_to_total_screen_orc(table_name, result["imp_python_class"], yestoday_str)
                pass
            else:  # 其他规则直接存到指定的表格中
                #self.copy_data_one_column(table_name, result["mongodb_tablename"], yestoday_str)
                level = int(result["level"])
                if level == 1:
                    self.copy_data_to_total(table_name, result["imp_python_class"], yestoday_str)
                else:
                    self.copy_data_to_total(table_name, result["mongodb_tablename"], yestoday_str)
                    pass
                pass
            result = cursor.fetchone()
        # 汇总所有的统计数据
        self.total_count(yestoday_str)
        cursor.close()
        conn.close()
        pass

    # 导入纯人工审核数据
    def batchImportManualData(self,tag):
        yestoday = LocalTime.from_today(self.time_go)
        yestoday_str = yestoday.strftime("%Y%m%d")
        runner_logs = self._database["runner_logs"+yestoday_str]

        yestoday_time = LocalTime.nowtime_str(-1).strftime("%Y-%m-%d %H:%M:%S")
        yestoday_nowtime = LocalTime.from_today(self.time_go).strftime("%Y-%m-%d %H:%M:%S")
        SingleLogger().log.debug("======yestoday_time=======>%s" % yestoday_time)
        SingleLogger().log.debug("======yestoday_nowtime=======>%s" % yestoday_nowtime)

        mongo_cursor = runner_logs.find({'time': {'$gte': yestoday_time, '$lte': yestoday_nowtime},"tag": tag})

        try:
            conn = MySQLHelper.pool_connection.get_connection()
            # 创建游标
            mysql_cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            for row in mongo_cursor:
                sql_str = """INSERT ignore INTO `analysis_data_normal_total`
                                (`res_id`,
                                `title`,
                                `description`,
                                `crawl_time`,
                                `XueXingBaoLiRule`,
                                `screenshot`,
                                `screen_index`,
                                `app_tag`,
                                `category_tag`,
                                `shorturl`,
                                `create_date`,
                                `SexyRule`,
                                `PoliticalRule`,
                                `ZongJiaoRule`,
                                `BiaoTiDangRule`)
                                VALUES
                                ('%s','%s','%s','%s',%d,'%s',%s,'%s','%s','%s','%s',%d,%d,%d,%d)
                                """ % (
                    Secret.md5(row["screenshot"]), "人工审核无标题","",
                    row["time"], 0, row["screenshot"], row["screen"],
                    row["tag"], row["reference"], "", yestoday_str, 0, 0, 0, 0)

                SingleLogger().log.debug(sql_str)
                row_count = mysql_cursor.execute(sql_str)
                #将数据插入到指定的处理消息队列(id，日期)
                RedisHelper.strict_redis.lpush("newslist", Secret.md5(row["screenshot"])+","+yestoday_str)

        except Exception as ex:
            SingleLogger().log.error(ex)
        finally:
            pass

        pass
    def run(self):
        self.tags = self.queryManualApp() # 查询人工审核的tags
        self.batchImportMachineData()
        for tag in self.tags:
            self.batchImportManualData(tag["tag"])
        pass
        # Push数据同步到MySql
        #self.batchImportPushata() lzq屏蔽的，已经改为统一处理了
        # 删除空数据
        yestoday = LocalTime.from_today(self.time_go)
        yestoday_str = yestoday.strftime("%Y%m%d")
        self.remove_all_empty_data(yestoday_str)

    #Push数据同步到MySql
    def batchImportPushata(self):
        yestoday_h = LocalTime.from_today(self.time_go).strftime("%H")
        SingleLogger().log.debug("======h=======>%s" % yestoday_h)  
        if yestoday_h == 00:
            # 跨天需要隔表查询
            yestoday_str = LocalTime.yestoday_str()
            yestoday_time = LocalTime.from_today(-1).strftime("%Y-%m-%d")+ " 23:00:00"
            yestoday_nowtime = LocalTime.from_today(-1).strftime("%Y-%m-%d") +" 24:00:00"
        else:
            yestoday_str = LocalTime.now_str()
            SingleLogger().log.debug("======day=======>%s" % yestoday_str)
            yestoday_time = LocalTime.nowtime_str(-1).strftime("%Y-%m-%d %H:%M:%S")
            yestoday_nowtime = LocalTime.from_today(self.time_go).strftime("%Y-%m-%d %H:%M:%S")
            SingleLogger().log.debug("======yestoday_time=======>%s" % yestoday_time)
            SingleLogger().log.debug("======yestoday_nowtime=======>%s" % yestoday_nowtime)

        runner_logs = self._database["push" + yestoday_str]
        mongo_cursor = runner_logs.find({'time': {'$gte': yestoday_time, '$lte': yestoday_nowtime}})
        try:
            conn = MySQLHelper.pool_connection.get_connection()
            # 创建游标
            mysql_cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            for row in mongo_cursor:
                sql_str = """INSERT ignore INTO `analysis_data_normal_total`
                              (`res_id`,
                              `title`,
                              `description`,
                              `crawl_time`,
                              `XueXingBaoLiRule`,
                              `screenshot`,
                              `screen_index`,
                              `app_tag`,
                              `category_tag`,
                              `shorturl`,
                              `create_date`,
                              `SexyRule`,
                              `PoliticalRule`,
                              `ZongJiaoRule`,
                              `BiaoTiDangRule`)
                              VALUES
                              ('%s','%s','%s','%s',%d,'%s',%s,'%s','%s','%s','%s',%d,%d,%d,%d)
                              """ % (
                    Secret.md5(row["imgfilename"]), row["msg"],"Push消息无详情",
                    row["time"], 0, row["imgfilename"], 1,
                    row["tag"], "", "", yestoday_str, 0, 0, 0, 0)

                SingleLogger().log.debug(sql_str)
                row_count = mysql_cursor.execute(sql_str)
                SingleLogger().log.debug(row_count)
                #将数据插入到指定的处理消息队列(id，日期)
                RedisHelper.strict_redis.lpush("newslist", Secret.md5(row["imgfilename"])+","+yestoday_str)

        except Exception as ex:
            SingleLogger().log.error(ex)
        finally:
            pass

        pass



    def news_reader(self, tag):
        # 先找到有哪些表需要归档的，可以从规则表找
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # 执行SQL，并返回收影响行数
        row_count = cursor.execute("""
                            SELECT res_id, concat('originnews', `create_date`) AS mongodb_table ,rule_tag  
                            FROM `analysis_data_total` 
                            where changed =1 and check_status = 1 and rule_tag = '%s'
                            and %s
                            """ % (tag,
                                   """date_format(check_time,'%Y-%m-%d') = date_format(adddate(now(),-1),'%Y-%m-%d')"""))
        # 获取所有数据
        result = cursor.fetchone()

        while result != None:
            table = self._database[result["mongodb_table"]]
            single = table.find_one({"identity": result["res_id"]})
            if single != None:
                content = single["content"]
                # pass
                yield result, content

            result = cursor.fetchone()
        cursor.close()
        conn.close()

    def news_reader2(self, tag):
        # 先找到有哪些表需要归档的，可以从规则表找
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # 执行SQL，并返回收影响行数
        row_count = cursor.execute("""
                            select * from ArticleNormalSample
                            """)
        # 获取所有数据
        result = cursor.fetchone()

        while result != None:
            yield result["content"]

            result = cursor.fetchone()
        cursor.close()
        conn.close()