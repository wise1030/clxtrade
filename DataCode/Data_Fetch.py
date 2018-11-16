#!/usr/bin/python
# -*- coding: utf-8 -*-

import mysql.connector as sqlc
from mysql.connector import errorcode
import pandas as pd
class sqlcfg(object):
    __host =None
    __port = None
    __user = None
    __pwd = None
    __dbname = None
    __m_cfgcoe = ['host','port','user','pwd','dbname']
    __m_cfg = {}

    def __init__(self):
        pass

    def setcfg(self,mcfg):
        self.__m_cfg = mcfg

    def getcfg(self):
        return self.__m_cfg

    def sethost(self,host):
        self.__host = host
        self.__m_cfg['host'] = host
    # def setport(self,port):
    #    self.__port = port
    #    self.__m_cfg['port'] = port
    def setuser(self,user):
        self.__user = user
        self.__m_cfg['user'] = user
    def setpwd(self,pwd):
        self.__pwd = pwd
        self.__m_cfg['password'] = pwd
    def setdb(self,db):
        self.__dbname = db
        self.__m_cfg['database'] = db
    def getdb(self):
        return self.__dbname
{'trade_date':1, 'pre_close':2, 'open':3, 'high':4, 'low':5, "close":6}

class data_connection(object):
    __dbcfg = None
    __sqldb = None
    __cursor = None
    __category = []
    def __init__(self):
        pass
    def connect(self,cfg):
        try:
            self.__sqldb = sqlc.connect(**cfg)
            self.__cursor = self.__sqldb.cursor()
        except sqlc.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            return 0

    def datafetch(self):
        pass
    def checkAlltables(self,dbname): #c查询数据库所有的表
        query = """select table_name from information_schema.tables where table_schema = '%s' and table_type ='base table'"""%(dbname)
        cursor = self.__sqldb.cursor()
        cursor.execute(query)
        return [each for each in cursor]

    def creatdatabase(self,dbname):#创建数据库
        # self.__sqldb.database = dbname
#       create = "CREATE DATABASE '%s' DEFAULT CHARACTER SET 'utf8'" %(dbname)
        create = "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(dbname)
        cursor = self.__sqldb.cursor()
        print dbname in self.showAllDatabase()

        if dbname in self.showAllDatabase():
            cursor.execute('drop database if exists ' + dbname)
        cursor.execute(create)
        self.__sqldb.commit()

    def showAllDatabase(self): #连接下的所有数据库
        cursor = self.__sqldb.cursor()
        cursor.execute("SHOW DATABASES")
        rows = cursor.fetchall()
        return ["%2s"% row for row in rows]

    def getallcatelog(self):
        return self.__category

    def getallkeysFortable(self,table):#查询指定表的所有字段名
        query = """select COLUMN_NAME from information_schema.COLUMNS where table_schema = 'future_information'and table_name = '%s' """ %(table)
        self.__cursor.execute(query)
        return [each[0] for each in self.__cursor]

    # 查询数据库指定表并转化成DateFrance格式
    def getdata(self,tablename):
        try:
            query = """SELECT * FROM %s WHERE (trade_date > cast('2018-9-1' as datetime) AND trade_date < cast('2019-1-1' as datetime))""" %tablename
            self.__cursor.execute(query)
        except:
            return
        result = self.__cursor.fetchall()
        if not result:
            return
        temDF =  pd.DataFrame(list(result))
        temDF.columns = self.getallkeysFortable(tablename)
        temDF.pop('id')
        temidx = temDF.pop('TRADE_DATE')
        temDF.index = list(temidx)
        return temDF
        #return list(result)
      #  for name,ddl in self.__sqldb.

def main():
    _m_cfg = sqlcfg()
    _m_cfg.sethost('192.168.16.23')
   # _m_cfg.setport('3306')
    _m_cfg.setuser('chen')
    _m_cfg.setpwd('bhrsysp')
    _m_cfg.setdb('future_information')
    m_sqldb = data_connection()
    m_sqldb.connect(_m_cfg.getcfg())
  #  m_sqldb.checkAlltables(_m_cfg.getdb())
    m_sqldb.showAllDatabase()
    dbname = u'future_information'
    #m_sqldb.creatdatabase(dbname)
    # cnx = sqlc.connect(host='192.168.16.23', user='chen', password='bhrsysp', database='future_information')
    # cursor = cnx.cursor()
    # query = ("""select table_name from information_schema.tables where table_schema = 'future_information'and table_type = 'base table'""")
    # cursor.execute(query)
    # for stm in cursor:
    #     print stm
    m_sqldb.getallkeysFortable('ru_daily')
    m_sqldb.getdata('ru_daily')


if __name__ == '__main__':
    main()