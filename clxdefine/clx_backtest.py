#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

class IStrategy(object):
    __m_position = None
    __m_data = None
    __m_order = None
    __m_trade = None
    __m_account = None
    def __init__(self):
        pass

    def getDataToDataFrame(self):
        pass

    def dataFilter(self):
        pass

    def loadStrategyCfg(self):
        pass

    def strategyBackTest(self):
        pass

    def getTraderesult(self):
        return self.__m_trade



class IPosition(object):
    __Instrument__ = None
    __LongPos__ = None
    __ShortPos__ =None
    __LongToday__ = None
    __ShortToday__ = None
    __VecPosDetails__ = []
    def getlongPos(self):
        return self.__LongPos__
    def getshortPos(self):
        return self.__LongPos__
    def getTodayshortPos(self):
        return self.__LongPos__
    def getTodaylongPos(self):
        return self.__LongPos__
    def getTodayPnl(self):
        pass

    def getTotalPnl(self):
        pass

    def getAveBuyPrice(self):
        pass

    def getAveSellPrice(self):
        pass

    def getAvePrice(self):
        pass

    def getTotalTradeShare(self):
        pass

    def getPosDetails(self):
        pass

    def addPosdetails(self, pos):
        self.__VecPosDetails__.append(pos)

    def Data2DataFrame(self):
        pass



class IOrder(object):
    __VecOrder__ = None
    __suspendingOrder__ = []
    def getTodayOrder(self):
        pass

    def getAllOrder(self):
        pass

    def addOrder(self):
        pass

    def setOrder(self):
        pass

    def deleteOrder(self, order):
        pass

    def getOrder(self, refid):
        self.__VecOrder__.find(refid)

class ITrade(object):
    pass

class PNLCalculate(object):
    pass