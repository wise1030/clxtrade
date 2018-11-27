#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

from DataCode.clx_wind import *
from DataCode.Data_Fetch import *
from clxdefine.clx_backtest import *
import talib as tb
import collections
import matplotlib.pyplot as plt
from sklearn import preprocessing
from arch import arch_model
class CommodityRank(IStrategy):
    InstrumentID = []
    InstrumentCfg = collections.OrderedDict()
    InitData = collections.OrderedDict()
    ordermap = None #强弱排序
    Dfshare = None
    group_flagmap = None # 强弱 组内划分 组内强为1，弱为-1
    group = [] #交易标的分组
    fpnl = None
    currcode = {}  # 当前交易合约的dict
    sharp_ratio = 0

    def __init__(self):
        pass
        #super(CommodityRank.self).__init__(self,)

    def loadcfg(self):
        with open("name_Contract.json", 'r') as load_f:
            Instrument = json.load(load_f)
        for key,item in Instrument.items():
            for it,value in item.items():
                if value[0] is True:
                    if key in [u'SHFE',u'DCE']:
                        a_code = it.lower()
                    else:
                        a_code = it.upper()
                    self.InstrumentID.append(a_code)
                    self.InstrumentCfg[a_code] = value
                    self.InstrumentCfg[a_code].append(key)
        #print self.InstrumentID, self.InstrumentCfg

    #连接数据库并下载数据
    def loaddata(self):
        self.loadcfg()
        dataDic = collections.OrderedDict()
        #dataDic = {}
        _m_cfg = sqlcfg()
        _m_cfg.sethost('192.168.16.23')
        # _m_cfg.setport('3306')
        _m_cfg.setuser('chen')
        _m_cfg.setpwd('bhrsysp')
        _m_cfg.setdb('future_information')
        m_sqldb = data_connection()
        m_sqldb.connect(_m_cfg.getcfg())
        self.setgroupmap()

        for id in self.InstrumentID:
            tem = m_sqldb.getdata(id.lower()+'_daily')
            if tem is None:
                continue
            else:
                dataDic[id] = tem.loc[:,['LOG_RETURN','OPEN','HIGH','LOW','CLOSE']]
                m_code = tem.iloc[-1]['TRADE_HISCODE'].split('.')[0]
                if id.islower():
                    self.currcode[id] = m_code.lower()
                else:
                    self.currcode[id] = m_code.upper()

        self.InitData = dataDic

    def loadStrategyCfg(self):
        pass

    def getrealtimequote(self):
        pass

    #强弱算法实现
    def algrithm_dsi(self,pse):
        return sum(pse)/sum(abs(pse))

    def algrithm_rsi(self,pse):
        return float((pse>0).sum())/float(len(pse))

    def df_array_normalize(self,pdf):
        pdfidx = pdf.index
        pdfcol = pdf.columns
        for ix in range(len(pdf.index)):
            if pdf.iloc[ix].isna().sum() < len(pdf.columns):
                pdf.iloc[ix].fillna(pdf.iloc[ix].median(),inplace = True)
            else:
                pdf.iloc[ix].fillna(0.0, inplace=True)
        pdf = preprocessing.scale(pdf,axis = 1)
        res =  pd.DataFrame(pdf,index = pdfidx,columns= pdfcol)
        return res

    def setgroupmap(self):
        grouplist = [['OI','y','p'],['rb','hc'],['m','RM'],['j','jm'],['pp','l'],['ag','au'],['IF','IH','IC'],['TF','T'],['SF','SM']]
        for ai in grouplist:
            if set(ai) < set(self.InstrumentID):#
                self.group.append(ai)

    def order_rank(self,coe1,coe2,coe3):
        #########################
        #index calculate##############################
        Index1 = collections.OrderedDict()
        Index2 = collections.OrderedDict()
        Index3 = collections.OrderedDict()
        Index4 = collections.OrderedDict()
        for key,it in self.InitData.items():
            it['DSI'] = 0
            it['DSI'] = it['LOG_RETURN'].rolling(coe1).apply(func = self.algrithm_dsi)
            it["RSI"] = it['LOG_RETURN'].rolling(coe2).apply(func = self.algrithm_rsi)
            it['STD'] = it['LOG_RETURN'].pow(2).ewm(min_periods=coe3,alpha = 0.07).mean().pow(0.5)
            it['DBS'] = it['LOG_RETURN']/it['STD']
            it['ADX'] = tb.ADX(np.array(it.HIGH),np.array(it.LOW),np.array(it.CLOSE),timeperiod = coe1)
            Index1[key] = it['DSI']
            Index2[key] = it['RSI']
            Index3[key] = it['STD']
            Index4[key] = it['LOG_RETURN']
        #print InitData['i_daily'].tail()#.shape[0],InitData.shape[1]
        DfIndex1 = pd.DataFrame(Index1)
        DfIndex2 = pd.DataFrame(Index2)
        DfIndex3 = pd.DataFrame(Index3)
        DfIndex4 = pd.DataFrame(Index4)
        ###标准化
        DfIndex1 = self.df_array_normalize(DfIndex1)
        DfIndex2 = self.df_array_normalize(DfIndex2)
        #DfIndex3 = self.df_array_normalize(DfIndex3)
        DfIndex4 = self.df_array_normalize(DfIndex4)
        #归一化
        #DfIndex3 = pd.DataFrame(preprocessing.minmax_scale(DfIndex3,axis = 1),DfIndex3.index,DfIndex3.columns)
        # GARCH estimate vol
        # for co in DfIndex3.columns:
        #     am = arch_model(DfIndex3[co])
        #     res = am.fit(update_freq=0)
        #     self.InitData[co]['GARCHVOL'] = res.conditional_volatility
        #print DfIndex3.tail(30)
        #print DfIndex4.tail(30)
        ##algorithm order strength
        #################################################################
        def DfOrder(df):
            idx = np.argsort(df,axis = 1)
            resOrderMap = idx.copy()
            resOrderMap.columns = range(idx.shape[1])
            #order shift dataframe
            for i in range(idx.shape[0]):
                sortix = 1
               # resOrdermap[idx.index[i]] = [ idx.ix[i]
                for x in idx.ix[i]:
                    idx.iloc[i,x] = sortix
                    resOrderMap.iloc[i,sortix - 1] = self.InitData.keys()[x]
                   # print InitData.keys()[x]
                    sortix = sortix + 1
            return idx, resOrderMap

        def DfOrder1(df):
            df.rank(methon = 'first',axis = 1)

        ##########   order    #################################
        idxmap,resOrderMap = DfOrder(DfIndex1*np.power(DfIndex2,2)) #+DfIndex2)
        self.ordermap = resOrderMap
        #print resOrderMap.tail(10), idx.tail(10)
        # deltaidx = idxmap - idxmap.shift(1) #cw*(idxmap - idxmap.shift(1)) + (1 - cw)*idxmap
        # shiftprt = idxmap.copy()
        # shiftprt.loc[:, :] = 0
        # nm = idxmap.shape[1]
        # deltaidx.fillna(0,inplace = True)
        # for i in range(1,idxmap.shape[0]):
        #     for x in idxmap.columns:
        #         if deltaidx.iloc[i][x] > 0:
        #             shiftprt.iloc[i][x] = deltaidx.iloc[i][x]/float(nm - idxmap.iloc[i - 1][x])
        #         elif deltaidx.iloc[i][x] > 0:
        #             shiftprt.iloc[i][x] = deltaidx.iloc[i][x] / float(idxmap.iloc[i - 1][x])
        #         else:
        #             if nm == idxmap.iloc[i - 1][x]:
        #                 shiftprt.iloc[i][x] = 1.0
        #             elif idxmap.iloc[i - 1][x] == 0:
        #                 shiftprt.iloc[i][x] = -1.0
        #             else:
        #                 shiftprt.iloc[i][x] = 0.0
        #
        # idxmapD, resOrderMapD = DfOrder(shiftprt)
        # ####
        # idxmap, resOrderMap = DfOrder(idxmapD + idxmap)
        # self.ordermap = resOrderMap

        #########    group inner order ############################
        self.group_flagmap = self.resbygroup(idxmap)
        #print self.group_sharemap.head(30)

        ########## order filtered by group #######################3
        sp,wp = self.marketsortbygroup(6)
        idx = idxmap.index
        col = idxmap.columns
        fltflag = idxmap.copy()
        fltflag.loc[:, :] = 0
        for ix in range(len(idx)):
            fltflag.iloc[ix][sp.iloc[ix]] = 1
            fltflag.iloc[ix][wp.iloc[ix]] = -1
        ########
        for cx in idxmap.columns:
            self.InitData[cx]['OrderRef'] = idxmap[cx]
            self.InitData[cx]['maOrderRef'] = idxmap[cx].rolling(3).mean()
            self.InitData[cx]['deltaOrder'] = idxmap[cx] - idxmap[cx].shift(1)

            self.InitData[cx]['normSTD'] = DfIndex3[cx]

            self.InitData[cx]['groupflag'] = self.group_flagmap[cx]
            self.InitData[cx]['fltflag'] = fltflag[cx]
        #####################################################

    def restoexcel(self,df_data,path):
        writer = pd.ExcelWriter(path)
        df_data.to_excel(writer,'Sheet1')
        writer.save()

    def resbygroup(self,ordermap):
        sharemap = ordermap.copy()
        sharemap.iloc[:,:] = 0
        for ix in range(len(ordermap.index)):
            for va in self.group:
                maxid = ordermap.iloc[ix][va].idxmax()
                minid = ordermap.iloc[ix][va].idxmin()
                sharemap.iloc[ix][maxid] = 1
                sharemap.iloc[ix][minid] = -1
        return sharemap

    def marketsortbygroup(self,num):
        glist = []
        for va in self.group:
            glist.extend(va)
        index = self.ordermap.index
        s_map = pd.DataFrame(columns = range(num), index=index)
        w_map = pd.DataFrame(columns = range(num), index=index)
        for ix in range(len(index)):
            i = 0
            for it in self.ordermap.iloc[ix]:
                if i >= num:
                    break
                if (it in glist and self.group_flagmap.iloc[ix][it] == -1) or it not in glist:
                    w_map.iloc[ix][i] = it
                    i += 1

        for ix in range(len(index)):
            i = 0
            for it in reversed(self.ordermap.iloc[ix]):
                if i >= num:
                    break
                if (it in glist and self.group_flagmap.iloc[ix][it] == 1) or it not in glist:
                    s_map.iloc[ix][i] = it
                    i += 1
        return s_map, w_map

    def calculateshare(self,m_var,rule):
        cat_n = len(self.InitData.keys())
        share = collections.OrderedDict()
        #rule basice
        def sharebasicrule(x,y):
            if x < 6:#or(x > 2*y/float(3) and x < y - 3):
                return -1 #* np.ceil(x/10.0)*3
            elif x > y - 5:#(x < y/float(3) and x > 3) or
                return 1#* np.ceil((y-x+1)/10.0)*3
            else:
                return 0
        if rule == 'basic':
            for key, va in self.InitData.items():
                ma = va['OrderRef'].shift(1)#+
                m_flag = ma.apply(lambda x:sharebasicrule(x,cat_n))
                share[key] = np.round(m_flag * m_var/(va['STD'].shift(1)*va['CLOSE'].shift(1)*self.InstrumentCfg[key][6])) #va['STD'].shift(1)*

        elif rule == 'groupin':
            for key, va in self.InitData.items():
                share[key] = np.round(va['groupflag'].shift(1) * m_var / (va['STD'].shift(1) * va['CLOSE'].shift(1) * self.InstrumentCfg[key][6]))

        elif rule == 'fltgroup':
            for key, va in self.InitData.items():
                share[key] = np.round(va['fltflag'].shift(1) * m_var / (va['STD'].shift(1) * va['CLOSE'].shift(1) * self.InstrumentCfg[key][6]))
            ##  print out trading share
            self.Dfshare = pd.DataFrame(share)
            trade_share = self.Dfshare - self.Dfshare.shift(1)
        return share

    #strategy1:full market monitor,fellow trading.........
    def calbacktestresult(self,share):
        #trading by orderRef / maOrderRef
        #################################################################################
        for key, va in self.InitData.items():
            va["daily_pnl"] = share[key]*va['LOG_RETURN']*va['CLOSE'].shift(1)*self.InstrumentCfg[key][6]
            va['deposit'] = share[key] * va['CLOSE'].shift(1) * self.InstrumentCfg[key][6] * 0.1
            va['cumpnl'] = va['daily_pnl'].cumsum(axis=0)

        ##print pnl InitData[key].tail(10)
        totalPNL = collections.OrderedDict()
        dailyPNL = collections.OrderedDict()
        for key in self.InitData:
            totalPNL[key] = self.InitData[key]['cumpnl']
            dailyPNL[key] = self.InitData[key]['daily_pnl']
        TPNL = pd.DataFrame(totalPNL)
        DPNL = pd.DataFrame(dailyPNL)
        TPNL['tpnl'] = TPNL.sum(axis = 1)
        DPNL['tdpnl'] = DPNL.sum(axis = 1)
        self.fpnl = TPNL
        self.sharp_ratio = DPNL['tdpnl'].mean()/DPNL['tdpnl'].std()
        print self.sharp_ratio

    def getfinalpos(self):
        return self.Dfshare.iloc[-1]

    def backtest(self):
        self.loaddata()
        daliyvar = 50000
        rule = 'fltgroup'
        coe = []
        dsiS = 8
        dsiE = 13
        rsiS = 6
        rsiE = 10
        volS = 8
        volE = 12
        re_optimize = np.empty((dsiE-dsiS, rsiE-rsiS, volE-volS))
        for dsi in range(dsiS,dsiE):
            for rsi in range(rsiS,rsiE):
                for vol in range(volS,volE):
                    self.order_rank(dsi,rsi,vol)
                    holdshare = self.calculateshare(daliyvar, rule)
                    self.calbacktestresult(holdshare)
                    lr = [dsi, rsi, vol, self.fpnl.iloc[-1,-1],self.sharp_ratio]
                    print lr
                    coe.append(lr)
                    re_optimize[dsi-dsiS][rsi-rsiS][vol-volS] = self.sharp_ratio#self.fpnl.iloc[-1,-1]

        midx = np.argwhere(re_optimize == re_optimize.max())
        coept = "C:\Users\Corin\Desktop\coeres1.xlsx"
        self.restoexcel(pd.DataFrame(coe), coept)
        print midx

    def backtest1(self):
        self.loaddata()
        dsi = 8#11
        rsi = 8#7
        vol = 9#10
        self.order_rank(dsi, rsi, vol)
        daliyvar = 10000
        rule = 'fltgroup'
        holdshare = self.calculateshare(daliyvar,rule)
        self.calbacktestresult(holdshare)
        self.logtofile()
    def logtofile(self):
        ###output result
        orderpath = "C:\Users\Corin\Desktop\ordermap.xlsx"
        self.restoexcel(self.ordermap,orderpath)
        sharept = "C:\Users\Corin\Desktop\shareres.xlsx"
        self.restoexcel(self.Dfshare, sharept)
        pnlpath = "C:\Users\Corin\Desktop\pnlres.xlsx"
        self.restoexcel(self.fpnl,pnlpath)
        self.fpnl.plot()#loc[:,self.InstrumentID]
        plt.show()


    def getlastprice(self):
        pass

    def updateprice(self):
        pass

    def pnlanalyzer(self):
        pass


def main():
    m_object = CommodityRank()
    m_object.backtest1()



if __name__ == '__main__':
        main()

