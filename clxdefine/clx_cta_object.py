import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import pandas as pd
import datetime


class DataCenter(object):
    keys = [u'openPrice', u'highPrice', u'lowPrice', u'closePrice', u'volume',u'log_return']
    def __init__(self, refresh_rate, pipe_length, symbol):
        self.data = {key:deque([], maxlen=pipe_length) for key in self.keys}
        self.refresh_rate = refresh_rate
        self.pipe_length = pipe_length
        self.symbol = symbol

    def update_data(self, symbol):

        if len(self.data['openPrice']) < self.pipe_length:
            hist = get_symbol_history(symbol=symbol, field=self.keys,
                                      time_range=self.refresh_rate*self.pipe_length)[symbol]
        else:
            hist = get_symbol_history(symbol=symbol, field=self.keys,
                                      time_range=self.refresh_rate)[symbol]
        current_data = {key:[] for key in self.keys}
        for i in range(int(len(hist)/self.refresh_rate)):
            current_bar = hist[self.pipe_length*i:self.pipe_length*i+self.refresh_rate]
            # if len(current_bar) ==0:
            #     break
            current_data['closePrice'].append(current_bar.ix[-1, 'closePrice'])
            current_data['openPrice'].append(current_bar.ix[0, 'openPrice'])
            current_data['highPrice'].append(current_bar['highPrice'].max())
            current_data['lowPrice'].append(current_bar['lowPrice'].min())
            current_data['volume'].append(current_bar['volume'].sum())
        for i in self.keys:
            self.data[i].extend(current_data[i]) 
        return self.data

    def clear(self):
        for i in self.keys:
            self.data[i].clear()
            
            
class Trans(object):

    def __new__(cls, account, symbol, datacenter, *args, **kwargs):

        if not hasattr(cls, '_instance'):

            instance = super(Trans, cls).__new__(cls, *args, **kwargs)

            instance.account = account
            instance.symbol = symbol
            instance.datacenter = datacenter
            cls._instance = instance
        return cls._instance 

    def replace(self, symbol):
        if self.symbol != symbol:
            long_position = self.account.position.get(self.symbol, dict()).get('long_position', 0)
            short_position = self.account.position.get(self.symbol, dict()).get('short_position', 0)

            if long_position != 0:
                print self.account.current_date, self.account.current_time, '�����л��� ƽ��'
                order(self.symbol, -long_position, 'close')
            if short_position != 0:
                print self.account.current_date, self.account.current_time, '�����л��� ƽ��'
                order(self.symbol, short_position, 'close')
            self.symbol = symbol
            for i in self.datacenter.data.keys():
                self.datacenter.data[i].clear()
                

class Signals(object):
    def __new__(cls, datacenter, account, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            instance = super(Signals, cls).__new__(cls, *args, **kwargs)
            instance.datacenter = datacenter
            instance.order_list = {'long_open':False, 'short_open':False,
                                   'long_close1':False,'short_close1':False,
                                   'long_close2':False,'short_close2':False}
            instance.account = account
            instance.stopLoss1 = 10000000
            instance.stopLoss2 = 0
            instance.Len = 7
            instance.cost1 = 10000000
            instance.cost2 = 0
            instance.data = None
            instance.bandRange = {}
            instance.DaySignal = {}
            instance.OpenPrice = {}
            cls._instance = instance
        return cls._instance

    def _getMS(self,datas):
        datas = np.array(filter(None,datas))
        diff = datas[1:]-datas[:-1]
        return 100*sum(diff)/float(sum(abs(diff))) if sum(diff) !=0 else 0

    def getDailyMS(self,symbol):
        ls = [int(x) for x in self.account.current_date.split('-')]
        enddate = datetime.date(*ls)
        begindate = enddate-datetime.timedelta(days=10)
        self.data=DataAPI.MktFutdGet(ticker=symbol,beginDate=str(begindate),endDate=str(enddate),
                                     field=['closePrice','openPrice','tradeDate','highestPrice',
                                            'lowestPrice','settlePrice'],pandas="1")
        
        if len(list(self.data['settlePrice'])[-5:-1]) < 3:
            ms=0
            ls=[1,1]
        else:
            ls=list(self.data['openPrice'][-5:-1])
            ls.append(list(self.data['openPrice'])[-1])
            ms = self._getMS(ls)
    
        return (ms,ls[-1]/float(ls[-2])-1)

    def getRange(self,symbol): 
        ms = self.getDailyMS(symbol)
        period = 4+1
        hh = max(self.data['highestPrice'][-period:-1])
        
        hc = max(self.data['closePrice'][-period:-1])
        lc = min(self.data['closePrice'][-period:-1])
        ll = min(self.data['lowestPrice'][-period:-1])
        
        if len(self.data['highestPrice'][-period:])<3:
            return(100000,100000,0)
        h2 = max(self.data['highestPrice'][-3:-1])
        l2 = min(self.data['lowestPrice'][-3:-1])
        return (max(hh-lc,hc-ll),h2,l2)

    def getOpen(self):
        return list(self.data['openPrice'])[-1]

    def getMomenSignal(self,price):
        up = False
        down = False
        momentum1 = (price[-1] + price[-2])-(price[-3] + price[-4])
        momentum2 = (price[-4] + price[-5])-(price[-7] + price[-8])

        if momentum1 > 8 and momentum1 > momentum2:
            up = True
        elif momentum1 < -8 and momentum1 < momentum2:
            down = True
        return {'up':up, 'down':down}

    def getDailySignal(self,symbol):
        today = self.account.current_date
        if self.DaySignal.get(today,None)==None:
            ms = self.getDailyMS(symbol)
            self.DaySignal = {}
            self.DaySignal[today] = {}
            self.DaySignal[today]['up'] = 80 > ms[0] > 30 or 8/100.0>ms[1]>3/100.0 
            self.DaySignal[today]['down'] = -80 < ms < -30 or -8/100.0 <ms[1]<-3/100.0
            self.OpenPrice = {}
            self.OpenPrice[today] = self.getOpen()
            self.bandRange = {}
            self.bandRange[today] = self.getRange(symbol)

        if not self.DaySignal[today]['up']:
            if list(self.datacenter.data['highPrice'])[-1] > self.OpenPrice[today]+K1* self.bandRange[today][0]:
                self.DaySignal[today]['up']  = True

        if not self.DaySignal[today]['down']:
            if list(self.datacenter.data['lowPrice'])[-1] < self.OpenPrice[today]-K2* self.bandRange[today][0]:
                self.DaySignal[today]['down'] = True

        return self.DaySignal[today]


    def signals_update(self,symbol):
        self._long_short_signals_update(symbol)

    def _long_short_signals_update(self,symbol):
        today = self.account.current_date
        day_signal = self.getDailySignal(symbol)

        close_price = np.array(self.datacenter.data['closePrice'])
        high_price = np.array(self.datacenter.data['highPrice'])
        low_price = np.array(self.datacenter.data['lowPrice'])

        ma=np.array(pd.rolling_mean(close_price,5))[-11:]
        # �����г�ǿ��
        ms = self._getMS(ma[1:]/ma[:-1]-1)
        ms1 = self._getMS(ma[-5:]/ma[-6:-1]-1)

        # ���㶯��
        momentum_signal = self.getMomenSignal(close_price)

        # ���������ڸߵ͵㣬���ڿ���ͻ��
        hh = max(high_price[-6:-1])+1
        ll = min(low_price[-6:-1])-1

        long_position = self.account.position.get(symbol, dict()).get('long_position', 0)
        short_position = self.account.position.get(symbol, dict()).get('short_position', 0)

        if ((ms > entry_strength1 or ms1>entry_strength2) and momentum_signal['up'] 
            and high_price[-1] >= hh and day_signal['up']):
            self.order_list['long_open'] = True
            self.order_list['short_close1'] = True
            if long_position ==0:
                self.cost1==close_price[-1]
                self.stopLoss1 =ll
        else:
            self.order_list['long_open'] = False
            self.order_list['short_close1'] = False

        if ((ms < -entry_strength1 or ms1<-entry_strength2) and 
            momentum_signal['down'] and low_price[-1] <= ll and day_signal['down']):

            self.order_list['short_open'] = True
            self.order_list['long_close1'] = True
            if short_position==0:
                self.cost2==close_price[-1]
                self.stopLoss2 = hh
        else:
            self.order_list['short_open'] = False
            self.order_list['long_close1'] = False

        if self.account.position:
            if (long_position and (close_price[-1]<self.stopLoss1 or
                                    close_price[-1]>self.cost1+PF*(self.cost1-self.stopLoss1))):
                self.order_list['long_close2'] = True
            else:
                self.order_list['long_close2'] = False

            if (short_position and (close_price[-1]>self.stopLoss2 or 
                                     close_price[-1]<self.cost2-PF*(self.stopLoss2-self.cost2))):
                self.order_list['short_close2'] = True
            else:
                self.order_list['short_close2'] = False
        else:
            self.order_list['short_close2'] = False
            self.order_list['long_close2'] = False
            
            
class Trader(object):
    def __new__(cls, account, signal, symbol, *args, **kwargs):

        if not hasattr(cls, '_instance'):

            instance = super(Trader, cls).__new__(cls, *args, **kwargs)

            instance.account = account
            instance.signal = signal
            instance.symbool = symbol
            cls._instance = instance
        return cls._instance

    def trade(self, symbol):
        price = get_symbol_history(symbol=symbol, field='closePrice',time_range=1)[symbol]['closePrice']
        long_position = self.account.position.get(symbol, dict()).get('long_position', 0)
        short_position = self.account.position.get(symbol, dict()).get('short_position', 0)
        
        if long_position and (self.signal.order_list['long_close1'] or self.signal.order_list['long_close2']) :
            order(symbol, amount = -1, offset_flag = 'close', direction = 'long')
            print 'long close',price[-1]
        if short_position and (self.signal.order_list['short_close1'] or self.signal.order_list['short_close2']):
            order(symbol, amount = -1, offset_flag = 'close', direction = 'short')
            print 'short close',price[-1]
        if long_position == 0 and self.signal.order_list['long_open']:
            order(symbol, amount = 1, offset_flag = 'open', direction = 'long')
            print 'long open',price[-1]
        if short_position == 0 and self.signal.order_list['short_open']:
            order(symbol, amount = 1, offset_flag = 'open', direction = 'short')
            print 'short open',price[-1]