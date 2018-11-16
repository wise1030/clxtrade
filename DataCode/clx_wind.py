#import xlwings as xw
from datetime import datetime
from time import *
from WindPy import w
from scipy import stats
from time import sleep
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
class WindData(object):
    begint = None
    endt = None
    beginDay = None
    endDay = None
    Fields = None
    freq = None  # 'm'--minutes; 'd'--day;
    w = w
    InstrumentID = ['RU1701.SHF']
    Data_Dict = {}    
  # xw = xw  
    def __init__(self):
        self.w.start()
        
    def setdate(self,beginday,endday):
        self.beginDay = beginday
        self.endDay = endday
    
    def settime(self,beginTime,endTime):
        try:
            tupleBegin = datetime.strptime(beginTime,'%Y-%m-%d %H:%M:%S')
            tupleEnd = datetime.strptime(endTime,'%Y-%m-%d %H:%M:%S')
            self.begint = beginTime
            self.endt = endTime
            self.beginDay = tupleBegin.strftime('%Y-%m-%d')
            self.endDay = tupleEnd.strftime('%Y-%m-%d')
        except:
            tupleBegin = datetime.strptime(beginTime,'%Y-%m-%d')
            tupleEnd = datetime.strptime(endTime,'%Y-%m-%d')
            self.begint = beginTime +' 00:00:00'
            self.endt = endTime + ' 00:00:00'
            self.beginDay = beginTime
            self.endDay = endTime           
         
    def setminuteFreq(self,m_freq):
        self.Barsize = m_freq
        
    def setField(self,fields):
        self.Fields = fields    
        
    def getminutebar(self,code,barsize = 1):
        return self.w.wsi(code,self.Fields,self.begint,self.endt,Barsize = barsize)
       
    def getdaybar(self,code):
        return self.w.wsd(code,self.Fields,self.beginDay,self.endDay)

    def getrealtimeprice(self,code):
        return self.w.wsq(code,self,Fields)
    
    def fileread(path):
        
        file_oj = open(path)
        try:
            f_txt = file_oj.readlines()
        finally:
            file_oj.close()
        return map(lambda x:x.split(),f_txt)
        
        
    def createBook(self):
        pass        
        
    def toxlw(self):
        pass
    
    def calculate(self):
        begintt ='2016-07-01 9:00:00'
        endtt = '2016-11-1 9:00:00'
        freq = 'm'        
        self.settime(begintt, endtt)
        self.setField('OPEN,HIGH,LOW,CLOSE')
        for ID in self.InstrumentID:
            m_code1 = ID        
            mB = self.getminutebar(m_code1)
            dData = self.getdaybar(m_code1)
            # mB._dict_()
            dpd = pd.DataFrame(data = np.mat(dData.Data).transpose(),columns=dData.Fields,index=dData.Times)
            OHSpread = np.array(dData.Data[0]) - np.array(dData.Data[1])
            OLSpread = np.array(dData.Data[0]) - np.array(dData.Data[2])
            dpd['OHSpread'] = OHSpread/np.array(dData.Data[0])
            dpd['OLSpread'] = OLSpread/np.array(dData.Data[0])
            dpd['maxside'] = np.max(np.abs(dpd[['OHSpread','OLSpread']]),1)
            ds = np.append(-OHSpread,OLSpread)
            print stats.scoreatpercentile(ds,75)
            plt.hist(ds)
            dpd[['OHSpread','OLSpread','maxside']].plot()
            plt.figure(figsize=(6, 5))
            plt.title(m_code1 + '')
            plt.plot(mB.Times,mB.Data[0],'b')
            plt.show()
    def trend_evl(self,freq):
        self.w.wsi
        

def main():
    wd = WindData()
    sleep(1)
    wd.calculate()


    
    
    
if __name__ =='__main__':
    main()