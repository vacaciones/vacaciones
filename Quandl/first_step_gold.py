# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 23:43:39 2016

@author: ialbuq01
"""

# -*- coding: utf-8 -*-
"""
Created on Fri May 06 15:50:23 2016

@author: Ian
"""


import pandas as pd
import numpy as np
import datetime as dt
import math
import matplotlib.pyplot as plt
import matplotlib
import itertools


import copy
import pandas.io.data as web
import Quandl

import datetime as dt
import csv

import pickle



matplotlib.style.use('ggplot')


def find_events(df_data):
        df_event = pd.DataFrame(np.zeros((df_data.shape)), columns = df_data.columns, index = df_data.index)
        for tick in df_data.columns:
            dailyReturn =  df_data[tick]/df_data[tick].shift(1) - 1 
            df_event[tick][(dailyReturn <= -0.018) & (dailyReturn >= -0.15)] = 1
        return df_event
            
def get_ticks(tickers):
    with open('symbols.txt', 'rU') as csvfile:
     orderreader = csv.reader(csvfile,delimiter=',')#,delimiter=','
     for row in orderreader:
        tickers.append(str(row[0]).replace(' ' ,''))
    return tickers
    
def get_from_quandl(source_type):
    #gold WGC/GOLD_DAILY_USD
    api = 'XzAMTSk6Y4DMWTDD3rFp'
    return Quandl.get(source_type, api_key = api)
    
def get_some_gold_data(stock_tickers = None, quandl_sources = None, quandl_tickers = None):
    if stock_tickers is None:
        stock_tickers =  ['SPY','ABX','GG','NEM','PLZL.ME'] #^GSPC
        print 'Standard stock tickers were selected, namely:'
        print stock_tickers
    
    if quandl_sources is None:                   
        quandl_sources = ['RATEINF/INFLATION_USA','FRED/DGS10', 'FRED/GS6M','WGC/GOLD_DAILY_USD']
        
        if quandl_tickers is None: 
            quandl_tickers = ['US_inflation','US_10Y','US_6M','gold']
                    

    df_prices = pd.DataFrame([])#, columns = tickers , index = pd.date_range(start= '01/01/2011', end = dt.datetime.today()))
    
    df_prices = load_price_data(df_prices,stock_tickers)
    
    for (quandl_counter,each_quandl_source) in enumerate(quandl_sources):
        df_prices[quandl_tickers[quandl_counter]] = Quandl.get(each_quandl_source)
        df_prices[quandl_tickers[quandl_counter]] = df_prices[quandl_tickers[quandl_counter]].fillna(method = 'ffill')
                                    
            
    
    #df_prices['US_Treasury'] = Quandl.get('USTREASURY/YIELD') 
    #tickers.append('US_Treasury')
    
    tickers = stock_tickers + quandl_tickers
    #pickle.dump(df_prices, open('gold_somePrices.p','wb')) 

    np_daily_return = np.zeros(df_prices.shape)*np.nan
    df_daily_return = pd.DataFrame(index = df_prices.index, columns = df_prices.columns)
    for (tick_number,tick) in enumerate(tickers):
        np_daily_return[:,tick_number] = df_prices[tick]/df_prices[tick].shift(1) - 1
        df_daily_return[tick] = df_prices[tick]/df_prices[tick].shift(1) - 1
        
       

    
    pickle.dump((df_prices,df_daily_return), open('gold_somePrices.p','wb')) 
    
    return (df_prices,df_daily_return)
    

def load_price_data(df_prices,tickers):
    #now let's load that data
    for tick in tickers:
        try:
            df_prices[tick] = web.DataReader(tick, data_source='yahoo',start= '01/01/1970', end = dt.datetime.today())['Close']    
        except:
            print 'Could not load: ' + tick
    return df_prices
    
    
def compute_correlation(df_prices = None,df_daily_return = None, windowSize = None, showPlot = False):
    if df_prices is None:
        print 'No price information was passed, hence no correlation can be calculated. Exiting!'
        return
    #if df_daily_return is None:
        
    if windowSize is None:
        windowSize = 180
        
        
        
    tickers = list(df_prices.keys().values)
    df_roll_corr = pd.rolling_corr(df_daily_return[tickers[0]],arg2 = df_daily_return[tickers[1]], window = windowSize)

    f, (ax, ax_corr_1) = plt.subplots(2, 1, sharex=True, figsize=(8, 6), dpi=350)


    #ax = plt.axes([.1,.55,0.8,.4])
    ax_right = ax.twinx() 
    plt.sca(ax_right)
    df_prices[tickers[1]].plot (color = 'darkgoldenrod')#, legend = True, label = tickers[1]
    plt.ylabel('Price ' + tickers[1] +' [USD]', color = 'darkgoldenrod')
    
    plt.sca(ax)
    plt.title(tickers[0] + ' & ' + tickers[1] + ' historical price and corr.')

    df_prices[tickers[0]].plot(color = 'black')#, legend = True, label = tickers[0]
    plt.ylabel('Price ' + tickers[0] +' [USD]', color =  'k')
    
    ax_inset = plt.axes([.2,.7,0.125,0.125])
    plt.sca(ax_inset)
    #this boy here shows that the daily returns are historically uncorrelated (since 1980's)
    plt.plot(df_daily_return[tickers[0]],df_daily_return[tickers[1]],'o',color = 'darkgoldenrod',markersize = 2)
    plt.xticks([])
    plt.yticks([])
    

    
    #ax_corr_1 = plt.axes([.1,.1,0.8,0.35])
    plt.sca(ax_corr_1)
    
    plt.plot(df_roll_corr.index,np.zeros(df_roll_corr.index.shape),color ='gray',linestyle ='-')
    df_roll_corr.plot(label = str(windowSize) +'d roll. corr.',color = 'darkgoldenrod',legend = True)
    plt.grid('on')
    plt.ylabel('Pearson correlation coefficient')
    
    max_xticks = 15
    xloc = plt.MaxNLocator(max_xticks)
    ax_corr_1.xaxis.set_major_locator(xloc)
    
    plt.savefig(tickers[0] + '_' + tickers[1] + '_correlation' + '.pdf',dpi=50)
    
    return df_roll_corr

    

            
def perform_event_analysis(df_event,df_price,daysBf, daysAfter):
    days = np.arange(-np.abs(daysBf),np.abs(daysAfter) + 1)
    ret_evnts = np.zeros((1,np.shape(days)[0]))
    df_data = df_price.copy()    
    event = df_event.copy()
    
    event.values[-daysAfter:,:] = 0
    event.values[0:daysBf + 1,:] = 0
    
    
    for j,tick in enumerate(df_data.columns):
        idx_events = event[tick][event[tick] == 1].index
        dailyReturn = df_data[tick]/df_data[tick].shift(1) - 1
        ret_tick = np.zeros((1,np.shape(days)[0]))
        
        for an_event in idx_events:
            get_loc = event[tick].index.get_loc(an_event)
            ret_i = dailyReturn[get_loc - daysBf: get_loc + daysAfter + 1]
            ret_evnts = np.vstack((ret_evnts,ret_i))
            ret_tick   = np.vstack((ret_tick,ret_i))
               
            
        ret_tick = ret_tick[1:]
        
        #get cummulative return
        idx = np.logical_not(np.isnan(ret_tick)) 
        ret_tick = np.cumprod(ret_tick[:,idx[0]] + 1, axis = 1)
        #print ret_evnts.shape[0]
        #normalize with respect to zeroth day in a pythonic way. days[0] = -number
        ret_tick =  (ret_tick.T / ret_tick[:, days[0]]).T
        mean_tick = np.mean(ret_tick, axis = 0) 
        std_tick = np.std(ret_tick, axis = 0)
        plt.figure()
        plt.axhline(y=1.0, xmin=days[0], xmax=days[-1], color='k')
        plt.errorbar(days,mean_tick,yerr = std_tick, fmt = '-',ecolor='#AAAAFF')
        plt.title(str(tick) + ':  # of events = ' + str(ret_tick.shape[0]))
        plt.tight_layout()
        plt.ylabel('Cumulative Return')
            
        
    plt.figure()    
    ret_evnts = ret_evnts[1:]
    idx_evnts = np.logical_not(np.isnan(ret_evnts)) 
    ret_evnts = np.cumprod(ret_evnts[:,idx_evnts[0]] + 1, axis = 1)
    ret_evnts =  (ret_evnts.T / ret_evnts[:, days[0]]).T     
    ret_mean = np.mean(ret_evnts,axis = 0)
    ret_std = np.std(ret_evnts, axis = 0)
    plt.axhline(y=1.0, xmin=days[0], xmax=days[-1], color='k')    
    plt.errorbar(days,ret_mean,yerr = ret_std, fmt = '-',ecolor='#AAAAFF')
   
    #plt.xticks(days)
    plt.title('Overall # of observations: ' + str(ret_evnts.shape[0]))
    plt.ylabel('Cumulative Return')
    return days, ret_evnts


(df_prices,df_daily_return) = get_some_gold_data()
#%%
tickers = list(df_prices.keys().values)

#miners =
gold_miner_tickers =  ['ABX','GG','NEM','PLZL.ME']
combinations_gold_miners = list(itertools.combinations(gold_miner_tickers,2))

#all possible binary combinations
all_combinations  = list(itertools.combinations(tickers,2))
for each_pair in all_combinations:
    compute_correlation(df_prices[[each_pair[0],each_pair[1]]],df_daily_return[[each_pair[0],each_pair[1]]], 90, True)




#start_date =  df_daily_return.index.searchsorted(dt.datetime(1970, 1, 1))
#end_date   =  df_daily_return.index.searchsorted(pd.to_datetime(df_daily_return.index[-1]))
#df_daily_return_sliced = df_daily_return.ix[start_date:end_date]
       













