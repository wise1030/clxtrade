#!/usr/bin/python
# -*- coding: utf-8 -*-
#from __future__ import absolute_import

from strategy_rank import CommodityRank
import sys
sys.path.append(r'D:\python project\python')
from python.trader.event.eventEngine import *
from trader.rhGateway import *
import pandas as pd
from datetime import datetime
import numpy as np

# CTA引擎中涉及到的交易方向类型
CLXORDER_BUY = u'买开'
CLXORDER_SELL = u'卖开'

CLXORDER_COVERBUY = u'买平'
CLXORDER_COVERSELL = u'卖平'
CLXORDER_LONG = u'买入'
CLXORDER_SHORT = u'卖出'
# 本地停止单状态
STOPORDER_WAITING = u'等待中'
STOPORDER_CANCELLED = u'已撤销'
STOPORDER_TRIGGERED = u'已触发'

def unicode2str(unicode):
    return unicode.encode('gbk')

class tradingplatform(object):
    m_ctpgw = None #ctp交易接口
    m_stra = None #策略
    updateData = {}
    lastPrice = {}
    traded = False
    isstrategy = False
    holdpos = {}
    EnupdatePrice = True

    def __init__(self):
        self.initstrategy()
        for it in self.redict.values():
            self.updateData[it] = False
        self.mainEvent = EventEngine2()
        self.mainEvent.start()
        self.m_ctpgw = RhGateway(self.mainEvent,'RH','Test')
        self.mainEvent.register(EVENT_TICK,self.processquote)
        self.mainEvent.register(EVENT_POSITION,self.processpos)
        self.mainEvent.register(EVENT_TRADE,self.processtrade)
        self.mainEvent.register(EVENT_TIMER,self.waittingfortrading)
        self.mainEvent.register(EVENT_ERROR,self.processerror)
        self.inittradingapi()

    def setConCfg(self):
        #strategy_rank parameters dsi rsi vol windows
        para = [8,8,9]
        return para

    def setupdatePrice(self,bl = False):
        self.isupdatePrice = bl

    def initstrategy(self):
        self.m_stra = CommodityRank()
        self.m_stra.loaddata()
        self.redict = {v.encode('gbk'): k for k, v in self.m_stra.currcode.items()}

    def inittradingapi(self):
        self.connectCTP()
        self.getrealtimequote()

    def getrealtimequote(self):
        subreq = VtSubscribeReq()
        for key,symbol in self.m_stra.currcode.items():
            subreq.symbol = symbol
            self.m_ctpgw.subscribe(subreq)
            sleep(0.1)

    def connectCTP(self):
        self.m_ctpgw.connect()
        #for symbol in ['rb1901','m1901','if1812']:

    def processquote(self,event):
        data = event.dict_['data']
        self.lastPrice[data.symbol] = pd.DataFrame({'OPEN':data.openPrice,'HIGH':data.highPrice,'LOW':data.lowPrice,'CLOSE':data.lastPrice}, index=[datetime.strptime(data.date,'%Y%m%d')])
        self.updateData[self.redict[data.symbol]] = True
        #print data.symbol + ':' + str(data.lastPrice)
        if self.updateData.values().count(True) == len(self.updateData.values()) - 1 and not self.isstrategy:
            self.getStragetyPos()
        else:
            return

    def processtrade(self,event):
        trade = event.dict_['data']

        # 更新持仓缓存数据
        if trade.symbol not in self.holdpos:
            posBuffer = self.holdpos.get(trade.symbol, None)
            if not posBuffer:
                posBuffer = PositionBuffer()
                posBuffer.vtSymbol = trade.vtSymbol
                self.holdpos[trade.symbol] = posBuffer
            self.holdpos[trade.symbol].updateTradeData(trade)

    def processpos(self,event):
        pos = event.dict_['data']
        if pos.symbol not in self.holdpos:
            tempos = PositionBuffer()
            tempos.vtSymbol = pos.symbol
            self.holdpos[pos.symbol] = tempos
        self.holdpos[pos.symbol].updatePositionData(pos)

    def getStragetyPos(self):  # 获得策略期望持仓
        if self.EnupdatePrice:
            for key,value in self.lastPrice.items():
                nkey = self.redict[key]
                self.m_stra.InitData[nkey].append(value)
                self.m_stra.InitData[nkey].iloc[-1]["LOG_RETURN"] =np.log(self.m_stra.InitData[nkey].iloc[-1]["CLOSE"]) - np.log(self.m_stra.InitData[nkey].iloc[-2]['CLOSE'])
        para = self.setConCfg()
        self.m_stra.order_rank(para[0],para[1],para[2])
        self.m_stra.calculateshare(30000,'fltgroup')

        self.isstrategy = True

    def waittingfortrading(self,event):

        if not self.istradingtime():
            return

        if (not (self.m_ctpgw.isGatewayReady and self.isstrategy)) or self.traded:
            return

        ##check rolling

        print "start to trade..."
        for key,va in self.redict.items():

            if key in self.holdpos:
                netOrd = self.m_stra.getfinalpos()[va] - (self.holdpos[key].longPosition - self.holdpos[key].shortPosition)
                print key + ':holdlong: ' + str(self.holdpos[key].longPosition) + ' holdshort:' + str(
                    self.holdpos[key].shortPosition) + ' order ' + str(netOrd)
            else:
                netOrd = self.m_stra.getfinalpos()[va]
                print key + ':holdlong: 0 holdshort: 0 order'  + str(netOrd)

            if netOrd == 0:
                continue

            if netOrd >0:
                self.sendOrder(key,CLXORDER_LONG,self.lastPrice[key]['CLOSE'][-1],int(abs(netOrd)))
            else:
                self.sendOrder(key, CLXORDER_SHORT, self.lastPrice[key]['CLOSE'][-1], int(abs(netOrd)))
            sleep(0.2)
        self.traded = True

    def sendOrder(self, vtSymbol, orderType, price, volume):
        """发单"""
        if vtSymbol not in self.redict:
            return

        contractInfo = self.m_stra.InstrumentCfg[self.redict[vtSymbol]]
        req = VtOrderReq()
        req.symbol = vtSymbol
        req.exchange = contractInfo[-1]
        req.price = price
        req.volume = volume

        # 获取持仓缓存数据
        posBuffer = self.holdpos.get(vtSymbol)

        # 设计为CTA引擎发出的委托只允许使用限价单
        req.priceType = PRICETYPE_LIMITPRICE

        # CTA委托类型映射
        if orderType == CLXORDER_BUY:
            req.direction = DIRECTION_LONG
            req.offset = OFFSET_OPEN

        elif orderType == CLXORDER_SELL:
            req.direction = DIRECTION_SHORT
            req.offset = OFFSET_OPEN

        elif orderType == CLXORDER_LONG:
            req.direction = DIRECTION_LONG
            if not posBuffer:
                req.offset = OFFSET_OPEN
            else:
                if posBuffer.shortPosition == 0:
                    req.offset = OFFSET_OPEN
                elif posBuffer.shortPosition >= volume:
                    if contractInfo[-1] != EXCHANGE_SHFE:
                        req.offset = OFFSET_CLOSE
                    else:
                        if posBuffer.shortYd >= volume:
                            req.offset = OFFSET_CLOSE
                        elif posBuffer.shortYd < volume and posBuffer.shortYd > 0:
                            req.offset = OFFSET_CLOSE
                            req.volume = posBuffer.shortYd
                            vtOrderID1 = self.m_ctpgw.sendOrder(req)  # 发单
                            req.offset = OFFSET_CLOSETODAY
                            req.volume = volume - posBuffer.shortYd
                            vtOrderID2 = self.m_ctpgw.sendOrder(req)  # 发单
                            return vtOrderID1 + vtOrderID2
                        else:
                            req.offset = OFFSET_CLOSETODAY
                else:
                    if contractInfo[-1] != EXCHANGE_SHFE:
                        req.offset = OFFSET_CLOSE
                        req.volume = posBuffer.shortPosition
                        vtOrderID1 = self.m_ctpgw.sendOrder(req)  # 发单
                        req.offset = OFFSET_OPEN
                        req.volume = volume - posBuffer.shortPosition
                        vtOrderID2 = self.m_ctpgw.sendOrder(req)  # 发单
                        return vtOrderID1 + vtOrderID2
                    else:
                        vtOrderID1 = ''
                        vtOrderID2 = ''
                        if posBuffer.shortToday > 0:
                            req.volume = posBuffer.shortToday
                            req.offset = OFFSET_CLOSETODAY
                            vtOrderID1 = self.m_ctpgw.sendOrder(req)  # 发单
                        if posBuffer.shortYd > 0:
                            req.volume = posBuffer.shortYd
                            req.offset = OFFSET_CLOSE
                            vtOrderID2 = self.m_ctpgw.sendOrder(req)  # 发单

                        req.volume = volume - posBuffer.shortPosition
                        req.offset = OFFSET_OPEN
                        tOrderID3 = self.m_ctpgw.sendOrder(req)  # 发单
                        return vtOrderID1 + vtOrderID2 + tOrderID3

        elif orderType == CLXORDER_SHORT:
            req.direction = DIRECTION_SHORT
            if not posBuffer:
                req.offset = OFFSET_OPEN
            else:
                if posBuffer.longPosition == 0:
                    req.offset = OFFSET_OPEN
                elif posBuffer.longPosition >= volume:
                    if contractInfo[-1] != EXCHANGE_SHFE:
                        req.offset = OFFSET_CLOSE
                    else:
                        if posBuffer.longYd >= volume:
                            req.offset = OFFSET_CLOSE
                        elif posBuffer.longYd < volume and posBuffer.longYd > 0:
                            req.offset = OFFSET_CLOSE
                            req.volume = posBuffer.longYd
                            vtOrderID1 = self.m_ctpgw.sendOrder(req)  # 发单
                            req.offset = OFFSET_CLOSETODAY
                            req.volume = volume - posBuffer.longYd
                            vtOrderID2 = self.m_ctpgw.sendOrder(req)  # 发单
                            return vtOrderID1 + vtOrderID2
                        else:
                            req.offset = OFFSET_CLOSETODAY
                else:
                    if contractInfo[-1] != EXCHANGE_SHFE:
                        req.offset = OFFSET_CLOSE
                        req.volume = posBuffer.longPosition
                        vtOrderID1 = self.m_ctpgw.sendOrder(req)  # 发单
                        req.offset = OFFSET_OPEN
                        req.volume = volume - posBuffer.longPosition
                        vtOrderID2 = self.m_ctpgw.sendOrder(req)  # 发单
                        return vtOrderID1 + vtOrderID2
                    else:
                        vtOrderID1 = ''
                        vtOrderID2 = ''
                        if posBuffer.longToday > 0:
                            req.volume = posBuffer.longToday
                            req.offset = OFFSET_CLOSETODAY
                            vtOrderID1 = self.m_ctpgw.sendOrder(req)  # 发单
                        if posBuffer.shortYd > 0:
                            req.volume = posBuffer.longYd
                            req.offset = OFFSET_CLOSE
                            vtOrderID2 = self.m_ctpgw.sendOrder(req)  # 发单

                        req.volume = volume - posBuffer.longPosition
                        req.offset = OFFSET_OPEN
                        tOrderID3 = self.m_ctpgw.sendOrder(req)  # 发单
                        return vtOrderID1 + vtOrderID2 + tOrderID3

        vtOrderID = self.m_ctpgw.sendOrder(req)  # 发单
        # self.writeCtaLog(u'策略发送委托，%s，%s，%s@%s'
        #                  % (vtSymbol, req.direction, volume, price))
        return vtOrderID

    def processerror(self,event):
        data = event.dict_['data']
        print str(data.errorID) + data.errorMsg

    def istradingtime(self):
        now_time = datetime.now()
        if now_time.hour > 14 and now_time.hour < 15 and now_time.minute > 57:
            return True
        else:
            return False

    def getholdpos(self):
        pass
    def calculateorder(self):
        pass
    def logorderinfo(self):
        pass
    def getstrategypnl(self):
        pass
    def writetodatebase(self):
        pass


class PositionBuffer(object):
    """持仓缓存信息（本地维护的持仓数据）"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.vtSymbol = EMPTY_STRING

        # 多头
        self.longPosition = EMPTY_INT
        self.longToday = EMPTY_INT
        self.longYd = EMPTY_INT

        # 空头
        self.shortPosition = EMPTY_INT
        self.shortToday = EMPTY_INT
        self.shortYd = EMPTY_INT

    # ----------------------------------------------------------------------
    def updatePositionData(self, pos):
        """更新持仓数据"""
        if pos.direction == DIRECTION_LONG:
            self.longPosition = pos.position
            self.longYd = pos.ydPosition
            self.longToday = self.longPosition - self.longYd
        else:
            self.shortPosition = pos.position
            self.shortYd = pos.ydPosition
            self.shortToday = self.shortPosition - self.shortYd

    # ----------------------------------------------------------------------
    def updateTradeData(self, trade):
        """更新成交数据"""
        if trade.direction == DIRECTION_LONG:
            # 多方开仓，则对应多头的持仓和今仓增加
            if trade.offset == OFFSET_OPEN:
                self.longPosition += trade.volume
                self.longToday += trade.volume
            # 多方平今，对应空头的持仓和今仓减少
            elif trade.offset == OFFSET_CLOSETODAY:
                self.shortPosition -= trade.volume
                self.shortToday -= trade.volume
            # 多方平昨，对应空头的持仓和昨仓减少
            else:
                self.shortPosition -= trade.volume
                self.shortYd -= trade.volume
        else:
            # 空头和多头相同
            if trade.offset == OFFSET_OPEN:
                self.shortPosition += trade.volume
                self.shortToday += trade.volume
            elif trade.offset == OFFSET_CLOSETODAY:
                self.longPosition -= trade.volume
                self.longToday -= trade.volume
            else:
                self.longPosition -= trade.volume
                self.longYd -= trade.volume

def main():
    m_trade = tradingplatform()

    while True:
        pass


if __name__ == '__main__':
        main()