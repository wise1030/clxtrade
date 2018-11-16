# coding: UTF-8
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import log,sqrt,exp
from scipy.stats import norm

class longstraddle(object):
    
    def __init__(self):
        parameters={}
        variants = {}
    
    def backtest(self,data,freq,):
        pass

    def call_option_pricer(self,spot,strike,maturity,rate,vol):
        d1=(log(spot/strike)+(rate+0.5*vol*vol)*maturity)/vol/sqrt(maturity)
        d2=d1-vol*sqrt(maturity)
        price=spot*norm.cdf(d1)-strike*exp(-rate*maturity)*norm.cdf(d2)
        return price 
    
    def put_option_pricer(self,spot,strike,maturity,rate,vol):  
        d1=(log(spot/strike)+(rate+0.5*vol*vol)*maturity)/vol/sqrt(maturity)
        d2=d1-vol*sqrt(maturity)
        price=spot*norm.cdf(d1)-strike*exp(-rate*maturity)*norm.cdf(d2) + strike*exp(-rate*maturity)-spot
        return price  
    
    def option_pricer(self,spot,strike,maturity,rate,vol,cp):
        d1=(log(spot/strike)+(rate+0.5*vol*vol)*maturity)/vol/sqrt(maturity)
        d2=d1-vol*sqrt(maturity) 
        
        if cp == 'call':
            price=spot*norm.cdf(d1)-strike*exp(-rate*maturity)*norm.cdf(d2)
        elif cp =='put':
            price=spot*norm.cdf(d1)-strike*exp(-rate*maturity)*norm.cdf(d2) + strike*exp(-rate*maturity)-spot
        return price  
    
    def blspricer(self,spot,strike,maturity,rate,vol,cp = 'call'):
        d1=(np.log(spot/strike)+(rate+0.5*vol*vol)*maturity)/vol/np.sqrt(maturity)
        d2=d1-vol*np.sqrt(maturity) 
    
        cprice=spot*norm.cdf(d1)-strike*np.exp(-rate*maturity)*norm.cdf(d2)
        if cp == 'call':
            return cprice
        elif cp == 'put':
            pprice=cprice + strike*np.exp(-rate*maturity)-spot
            return pprice
        else:
            return 'option type is error'
    
    def blsdelta(self,spot,strike,maturity,rate,vol,cp='call'):
        d1=(np.log(spot/strike)+(rate+0.5*vol*vol)*maturity)/vol/np.sqrt(maturity)
        d2=d1-vol*np.sqrt(maturity)        
        if cp == 'call':
            return norm.cdf(d1)
        
        elif cp == 'put':
            return norm.cdf(d1) - 1.0
        
        else:
            print 'option type is error'        
    
    
    def blsgamma(self,spot,strike,maturity,rate,vol,cp = None):
        d1=(np.log(spot/strike)+(rate+0.5*vol*vol)*maturity)/vol/np.sqrt(maturity)
        d2=d1-vol*np.sqrt(maturity)            
        if(vol > 1e-8):
            return norm.pdf(d1)/(spot*vol*np.sqrt(maturity))
        else:
            return 0.0
    
    def blsvega(self,spot,strike,maturity,rate,vol,cp = None):
        d1=(np.log(spot/strike)+(rate+0.5*vol*vol)*maturity)/vol/np.sqrt(maturity)
        d2=d1-vol*np.sqrt(maturity)            
        return norm.pdf(d1)*spot*sqrt(maturity)
    
    
    def blstheta(self,spot,strike,maturity,rate,vol,cp = 'call'):
        d1=(np.log(spot/strike)+(rate+0.5*vol*vol)*maturity)/vol/np.sqrt(maturity)
        d2=d1-vol*np.sqrt(maturity)            
        if cp =='call':
            return -spot*norm.pdf(d1)*vol/2.0/np.sqrt(maturity) - rate*strike*exp(-rate*maturity)*norm.cdf(d1-vol*np.sqrt(maturity))
        elif cp =='put':
            return -spot*norm.pdf(d1)*vol/2.0/np.sqrt(maturity) + rate*strike*exp(-rate*maturity)*norm.cdf(-d1+vol*np.sqrt(maturity))
        else:
            print 'option type is error'
    
    def blsimpv(self,spot,strike,maturity,rate,vol,cp = None):
        return_vol = 0.5
        estimateP = option_pricer()
        
    def setspacer(self,spot,ratio):
        ordv = [j*pow(10,i) for i in range(-5,6) for j in [1,2,5]]
        for idx in range(len(ordv)-1):
            if (spot*ratio - ordv[idx])*(ordv[idx+1]- spot*ratio) >= 0:
                if spot*ratio - ordv[idx] < ordv[idx+1]- spot*ratio:
                    return ordv[idx]
                else:
                    return ordv[idx+1]
    
    def setstrikelist(self,spot,spacer,num):
        sti = int(spot/spacer) 
        downsidestrike = spacer*np.arange(sti-int(num/2.0)+1,sti+1)
        upsidestrike = spacer*np.arange(sti+1,sti+int(num/2.0)+1)
        strikelist = np.append(np.append(downsidestrike,spot),upsidestrike)
        return strikelist
    
    def setspotmove(self,spot,MaxMovePrt):
        ml = np.linspace(1-MaxMovePrt,1+MaxMovePrt)
        return spot*ml,ml
        
    def settimedecay(self,virtualPeriod,tradminute,bartime):
        td = int(tradminute/bartime)
        ordertime = virtualPeriod/256.0*np.arange(td)/td+0.5/256
        timeflag = ordertime[::-1]
        return timeflag
    
    def setvolmove(self,vol,minmove,num):
        return np.append(vol*np.arange(stop))    
        
    def scenario(self,spot):
        pass   
    
    def rtoxlw(self,result):
        pass
        
    def showresult(self,result):
        pass        
        
def main():
    ob = longstraddle()
    
    spot = 11356.0
    spacer = ob.setspacer(spot, 0.01)
    num = 20
    strike = ob.setstrikelist(spot, spacer, num)
    ir = 0.0225
    vol = 0.25
    mt = 0.01    
    a = ob.blspricer(spot, strike, mt, ir, vol)    
    print 'test formula is' , a
    cdelta = ob.blsdelta(spot, strike, mt, ir, vol, 'call')
    pdelta = ob.blsdelta(spot, strike, mt, ir, vol, 'put')
    gamma = ob.blsgamma(spot, strike, mt, ir, vol)
    vega = ob.blsvega(spot, strike, mt, ir, vol)   
    ctheta = ob.blstheta(spot, strike, mt, ir, vol, 'call')
    ptheta = ob.blstheta(spot, strike, mt, ir, vol, 'put')
    print 'test greeks ,delta is:', cdelta,pdelta
    xaxis = strike/spot

    fig,ax = plt.subplots(3,2)

    ax[0][0].plot(xaxis,cdelta)
    ax[0][1].plot(xaxis,pdelta)
    ax[1][0].plot(xaxis,gamma)
    ax[1][1].plot(xaxis,vega)
    ax[2][0].plot(xaxis,ctheta)
    ax[2][1].plot(xaxis,ptheta)
    m=ax.ravel().tolist()
    [i.grid() for i in m]
       
    
    
    
    fixstrike = spot*0.99
    tensor = ob.settimedecay(1, 240, 3)
    print tensor
    cdelta1 = ob.blsdelta(spot, fixstrike, tensor, ir, vol, 'call')
    pdelta1 = ob.blsdelta(spot, fixstrike, tensor, ir, vol, 'put')
    straddledelta = cdelta1+pdelta1
    deltatest = pd.DataFrame({'cdelta1':cdelta1,'pdelta1':pdelta1,'total':straddledelta})  
    
    deltatest.plot()
    fig2,ax1 = plt.subplots(2,2)    
    fixstrike2 = spot
    spot2 = np.linspace(1,1.05)*spot
    mt = 1/256.0
    cdelta2 = ob.blsdelta(spot2, fixstrike2, mt, ir, vol, 'call')
    pdelta2 = ob.blsdelta(spot2, fixstrike2, mt, ir, vol, 'put')  
    straddledelta2 = cdelta2+pdelta2
    deltatest2 = pd.DataFrame({'cdelta1':cdelta2,'pdelta1':pdelta2,'total':straddledelta2}) 
    deltatest2.plot()    
    
    plt.show()
    
    

if __name__ =='__main__':
    main()
    
    
    
