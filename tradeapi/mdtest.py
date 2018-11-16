# encoding: UTF-8

import sys
import os
import json
from copy import copy
from datetime import datetime
from python.trader.ctp import MdApi, TdApi, defineDict
from python.trader.vtGateway import *
from python.trader.vtFunction import getJsonPath, getTempPath
from python.trader.vtConstant import GATEWAYTYPE_FUTURES
from python.trader.language import text
from vtObject import *
from time import sleep
from PyQt4 import QtGui
#----------------------------------------------------------------------
def print_dict(d):
    """按照键值打印一个字典"""
    for key,value in d.items():
        print key + ':' + str(value)
        
        
#----------------------------------------------------------------------
def simple_log(func):
    """简单装饰器用于输出函数名"""
    def wrapper(*args, **kw):
        print ""
        print str(func.__name__)
        return func(*args, **kw)
    return wrapper


########################################################################
class TestMdApi(MdApi):
    """测试用实例"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(TestMdApi, self).__init__()
        
    #----------------------------------------------------------------------
    @simple_log    
    def onFrontConnected(self):
        """服务器连接"""
        loginReq = {}  # 创建一个空字典
        loginReq['UserID'] = "049641"  # 参数作为字典键值的方式传入
        loginReq['Password'] = 'cc103000'  # 键名和C++中的结构体成员名对应
        loginReq['BrokerID'] = '9999'
        reqid =  1  # 请求数必须保持唯一性
        i = self.reqUserLogin(loginReq, 1)
        print 'Front Connected'
    
    #----------------------------------------------------------------------
    @simple_log    
    def onFrontDisconnected(self, n):
        """服务器断开"""
        print n
        
    #----------------------------------------------------------------------
    @simple_log    
    def onHeartBeatWarning(self, n):
        """心跳报警"""
        print n
    
    #----------------------------------------------------------------------
    @simple_log    
    def onRspError(self, error, n, last):
        """错误"""
        print_dict(error)
    
    @simple_log 
    #----------------------------------------------------------------------
    def onRspUserLogin(self, data, error, n, last):
        """登陆回报"""
        print_dict(data)
        print_dict(error)
        
    #----------------------------------------------------------------------
    @simple_log    
    def onRspUserLogout(self, data, error, n, last):
        """登出回报"""
        print_dict(data)
        print_dict(error)
        
    #----------------------------------------------------------------------
    @simple_log    
    def onRspSubMarketData(self, data, error, n, last):
        """订阅合约回报"""
        print_dict(data)
        print_dict(error)
        
    #----------------------------------------------------------------------
    @simple_log    
    def onRspUnSubMarketData(self, data, error, n, last):
        """退订合约回报"""
        print_dict(data)
        print_dict(error)    
        
    #----------------------------------------------------------------------
    @simple_log    
    def onRtnDepthMarketData(self, data):
        """行情推送"""
        print_dict(data)
    
    #----------------------------------------------------------------------
    @simple_log    
    def onRspSubForQuoteRsp(self, data, error, n, last):
        """订阅合约回报"""
        print_dict(data)
        print_dict(error)
        
    #----------------------------------------------------------------------
    @simple_log    
    def onRspUnSubForQuoteRsp(self, data, error, n, last):
        """退订合约回报"""
        print_dict(data)
        print_dict(error)    
        
    #----------------------------------------------------------------------
    @simple_log    
    def onRtnForQuoteRsp(self, data):
        """行情推送"""
        print_dict(data)    


#----------------------------------------------------------------------
def main():
    """主测试函数，出现堵塞时可以考虑使用sleep"""
    reqid = 0
    
    # 创建Qt应用对象，用于事件循环
    app = QtGui.QApplication(sys.argv)

    # 创建API对象
    api = TestMdApi()
    
    # 在C++环境中创建MdApi对象，传入参数是希望用来保存.con文件的地址
    api.createFtdcMdApi('')
    
    # 注册前置机地址
    # api.registerFront("tcp://180.168.146.187:10011")
    api.registerFront("tcp://180.168.146.187:10031")

    # 初始化api，连接前置机
    api.init()
    sleep(0.5)
    
    # 登陆
    # loginReq = {}                           # 创建一个空字典
    # loginReq['UserID'] = "049641"                 # 参数作为字典键值的方式传入
    # loginReq['Password'] = 'cc103000'               # 键名和C++中的结构体成员名对应
    # loginReq['BrokerID'] = '9999'
    # reqid = reqid + 1                       # 请求数必须保持唯一性
    # i = api.reqUserLogin(loginReq, 1)
    sleep(0.5)
    
    ## 登出，测试出错（无此功能）
    #reqid = reqid + 1
    #i = api.reqUserLogout({}, 1)
    #sleep(0.5)
    
    ## 安全退出，测试通过
    #i = api.exit()
    
    ## 获取交易日，目前输出为空
    #day = api.getTradingDay()
    #print 'Trading Day is:' + str(day)
    #sleep(0.5)
    
    ## 订阅合约，测试通过
    i = api.subscribeMarketData('a1901')
    
    ## 退订合约，测试通过
    #i = api.unSubscribeMarketData('IF1505')
    
    # 订阅询价，测试通过
    i = api.subscribeForQuoteRsp('IO1504-C-3900')
    
    # 退订询价，测试通过
    i = api.unSubscribeForQuoteRsp('IO1504-C-3900')
    
    # 连续运行，用于输出行情
    app.exec_()
    
    
    
if __name__ == '__main__':
    main()
