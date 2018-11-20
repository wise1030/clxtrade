#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


class clxStraTemplate(object):
    ##parameters
    __paraNameList__ = []
    __paraValue__ = []
    ##Variable
    __FactorList__ = []
    def __init__(self):
        pass
##策略初始化
    def InitStrategy(self):
        pass
##加载历史数据
    def loadHistoryData(self):
        pass
##数据整理
    def calibrateData(self):
        pass
##更新行情数据
    def updateHisData(self):
        pass
##加载策略参数
    def loadStraCfg(self):
        pass
##计算所有因子
    def calculateFactor(self):
        pass
##因子算法
    def factorAlgorithm(self):
        pass
##交易实现
    def papertradingbyfactor(self):
        pass
##计算交易结果、盈亏、pnl、保证金
    def caltradingRes(self):
        pass
##交易绩效分析
    def resAnalysis(self):
        pass
##参数优化
    def para_optimize(self):
        pass
##结果输出、保存
    def logRes(self):
        pass


