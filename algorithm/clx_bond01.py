#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from clx_wind import *

import matplotlib.pyplot as plt
import numpy as np

class clxbond(object):
    DataPort = None
    def __init__(self):
        self.DataPort = WindData()

    def convert_2y_ytm(self,price):
        return np.irr([price,3,103])

    def convert_5y_ytm(self,price):
        return np.irr([price, 3, 3, 3, 3, 103])

    def convert_10y_ytm(self,price):
        return np.irr([price, 3, 3, 3, 3, 3, 3, 3, 3, 3, 103])

    def get_windData(self):
        self.DataPort.settime('2018-06-01 9:00:00','2018-11-01 16:00:00')
        self.DataPort.setField('close')
     #   _md_2y = self.DataPort.getminutebar('TS1812.CFE',15)
        _md_5y = self.DataPort.getminutebar('TF1812.CFE',15)
        _md_10y = self.DataPort.getminutebar('T1812.CFE',15)
        a = [2*px for px in _md_5y.Data]
        print _md_5y.Data[0]
      #  _YTM_2y = [self.convert_2y_ytm(-px) for px in _md_2y.Data[0]]
        _YTM_5y = [self.convert_5y_ytm(-px) for px in _md_5y.Data[0]]
        _YTM_10y = [self.convert_10y_ytm(-px) for px in _md_10y.Data[0]]

        return [_YTM_10y,_YTM_5y]
    def calculate_d_(self):
        pass

    def plt_ytm(self):
        relt = self.get_windData()
        plt.figure(figsize=(6, 5))
        plt.plot(np.array(relt[0]) - np.array(relt[1]))
        print np.array(relt[0]) - np.array(relt[1])
        plt.grid()
        plt.show()

def main():
    m_bond  =  clxbond()
    m_bond.plt_ytm()

if __name__ == '__main__':
    main()