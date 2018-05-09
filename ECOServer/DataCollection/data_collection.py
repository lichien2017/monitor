
from pymongo import MongoClient
from threading import Thread
import pymysql
from util import *
from mysqldb.mysql_helper import MySQLHelper


class Collector(Thread):
    time_go = -1
    def __init__(self):
        Thread.__init__(self)
        self._client = MongoClient(ConfigHelper.mongodbip, ConfigHelper.mongodbport)
        self._database = self._client["crawlnews"]
        self.thread_stop = False
        pass
    # 处理单列的有害数据
    def copy_data_one_column(self,table_name,rule_tag,date):
        if table_name == None:
            SingleLogger().log.debug("table_name is None")
            return
        table = self._database[table_name]
        rows = table.find() # 查询出所有数据
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        for row in rows :
            res = self.get_resource(date, row["res_id"])
            if res == None:
                SingleLogger().log.error("resid = %s,没有找到详情信息，所以跳过"% row["res_id"])
                continue
            # insert_sql =
            # 执行SQL，并返回收影响行数
            try:
                row_count = cursor.execute("""insert into `analysis_data_total`(`res_id`,`create_date`,`rule_tag`,`app_tag`,
                                `category_tag`,`deleted`,`title`,`description`,`shorturl`,`changed`,`crawl_time`)
                                VALUES('%s','%s','%s','%s','%s',0,'%s','%s','%s',0,'%s')  ON DUPLICATE Key UPDATE res_id = '%s'
                             """ % (row["res_id"],date,rule_tag,res["app_tag"],res["category_tag"],pymysql.escape_string(res["title"]),
                                    pymysql.escape_string(res["description"]),res["shorturl"],res["crawltimestr"],row["res_id"]))
                conn.commit()
                SingleLogger().log.debug(row)
            except Exception as e:
                SingleLogger().log.error(e)
            pass
        cursor.close()
        conn.close()
        pass

    def get_resource(self,date,res_id):
        res_table = self._database["originnews%s" % date]
        res = res_table.find_one({"identity": res_id})
        return res
        pass
    # 处理ORC的数据，识别资源是第几屏幕
    def copy_data_screen_orc(self,table_name,rule_tag,date):
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
                if res == None :
                    continue
                # insert_sql =
                # 执行SQL，并返回收影响行数,'%s'
                # SingleLogger().log.debug("""insert into `analysis_data_total`(`res_id`,`create_date`,`rule_tag`,`screenshot`,
                #                   `screen_index`,
                #                   `app_tag`,`category_tag`,`deleted`,`title`,`description`,`shorturl`,`changed`,`crawl_time`)
                #                         VALUES('%s','%s','%s','%s','%s','%s','%s',0,'%s','%s','%s',0,'%s')
                #                         ON DUPLICATE Key UPDATE res_id = '%s'
                #                      """ % (row["res_id"], date, rule_tag, row["image"],row["screen_index"],
                #                             res["app_tag"],res["category_tag"],res["title"],res["description"],
                #                             res["shorturl"],res["crawltimestr"],row["res_id"]))
                row_count = cursor.execute("""insert into `analysis_data_total`(`res_id`,`create_date`,`rule_tag`,`screenshot`,
                                  `screen_index`,
                                  `app_tag`,`category_tag`,`deleted`,`title`,`description`,`shorturl`,`changed`,`crawl_time`)
                                        VALUES('%s','%s','%s','%s','%s','%s','%s',0,'%s','%s','%s',0,'%s')  
                                        ON DUPLICATE Key UPDATE res_id = '%s'
                                     """ % (row["res_id"], date, rule_tag, row["image"],row["screen_index"],
                                            res["app_tag"],res["category_tag"],pymysql.escape_string(res["title"]),pymysql.escape_string(res["description"]),
                                            res["shorturl"],res["crawltimestr"],row["res_id"]))
                conn.commit()
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
                delete from `analysis_data_total`
                where create_date = '%s'
                """ % (date))
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
        select count(distinct res_id) as ct from `analysis_data_total`
where create_date = '%s' and rule_tag <> 'screencapocr' 
        """% (date))
        result = cursor.fetchone()
        bad_count = result["ct"]
        # 总条数
        table = self._database["originnews" + date]
        count = table.count()
        # 删除数据
        row_count = cursor.execute("""
        delete from `analysis_collectCount`
        where create_date = '%s'
                """ % (date))
        # 执行SQL，并返回收影响行数
        row_count = cursor.execute("""
        insert into `analysis_collectCount`(`create_date`,`bad_count`,`count`)
        values('%s',%d,%d) 
        """ % (date,bad_count,count))

        cursor.close()
        conn.close()
        pass
    def run(self):
        # 先找到有哪些表需要归档的，可以从规则表找
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # 执行SQL，并返回收影响行数 select * from analysis_rules where level = 1 and isonline = 1
        row_count = cursor.execute("select * from analysis_rules")
        # 获取所有数据
        result = cursor.fetchone()
        yestoday = LocalTime.from_today(self.time_go)
        yestoday_str = yestoday.strftime("%Y%m%d")
        self.remove_all_table_data(yestoday_str)
        while result != None:
            SingleLogger().log.debug(result)
            table_name = "%s%s" % (result["mongodb_tablename"],yestoday_str)
            SingleLogger().log.debug("table_name is %s",table_name)

            if result["mongodb_tablename"].startswith("screencapocr") : #如果是判断第几屏幕，单独处理
                self.copy_data_screen_orc(table_name,result["mongodb_tablename"],yestoday_str)
                pass
            else: #其他规则直接存到指定的表格中
                self.copy_data_one_column(table_name,result["mongodb_tablename"],yestoday_str)
                pass
            result = cursor.fetchone()
        # 汇总所有的统计数据
        self.total_count(yestoday_str)
        cursor.close()
        conn.close()
        pass

    def test(self):
        # 先找到有哪些表需要归档的，可以从规则表找
        conn = MySQLHelper.pool_connection.get_connection()
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        # 执行SQL，并返回收影响行数
        row_count = cursor.execute("""
        SELECT
	res_id,
	'originnews' + `create_date` AS mongodb_table
FROM
	`analysis_data_total`
where changed =1 and check_status = 1 and date_format(check_time,'%Y-%m-%d') = date_format(adddate(now(),-1),'%Y-%m-%d')
        """)
        # 获取所有数据
        result = cursor.fetchone()

        while result != None:
            table = self._database[result["mongodb_table"]]
            single = table.find_one({"identity":result["res_id"]})
            if single != None:
                content = single["content"]
                pass
            result = cursor.fetchone()
        cursor.close()
        conn.close()
        pass