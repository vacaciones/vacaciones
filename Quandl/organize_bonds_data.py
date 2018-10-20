# -*- coding: utf-8 -*-
"""
Created on Sat Aug 06 13:52:21 2016

@author: ialbuq01
"""

#get brazillian bonds from debentures.com.br (anbima)

import pandas as pd
import pandas.io.data as web
from string import maketrans
import numpy as np
from xlrd import open_workbook
import pickle

from re import sub
from decimal import Decimal
import math
import matplotlib.pyplot as plt
import copy

import datetime as dt


f = open('debentures.txt')
data = f.readlines()[2:]
f.close()

#this data is structured as follows: (date,company,code,isinN,volume,transactions,minPrice,medPrice,maxPrice,percPU)
#our data will be a list of companies each representaded by dictionaries. Each item in a dictionary will be a  pandas object corresponding to a debt security!

ls_companies = [] #list
companies = []


pd_security = pd.DataFrame([])#pandas

for row,a_line in enumerate(data[1:]):
    #first get the info
    (date,company,code,isinN,volume,transactions,minPrice,medPrice,maxPrice,percPU) = a_line.strip().split('\t')

    try:
        Pperc = float(percPU[1:-1].replace(',' ,'.'))
    except ValueError:
        Pperc = np.nan
        
    try:   
        Pmin = float(Decimal(sub(r'[^\d.]', '', minPrice[1:-1].translate(maketrans('.,',',.')))))
        Pmed = float(Decimal(sub(r'[^\d.]', '', medPrice[1:-1].translate(maketrans('.,',',.')))))
        Pmax = float(Decimal(sub(r'[^\d.]', '', maxPrice[1:-1].translate(maketrans('.,',',.')))))
    except:   
        Pmin = float(Decimal(sub(r'[^\d.]', '', minPrice[1:-1]))*1000)
        Pmed = float(Decimal(sub(r'[^\d.]', '', medPrice[1:-1]))*1000)
        Pmax = float(Decimal(sub(r'[^\d.]', '', maxPrice[1:-1]))*1000)
        
        
        
        
        
    debt_instrument = code
    ls_values = [float(volume),float(transactions),Pmin,Pmed,Pmax,Pperc]
    dt_date = dt.datetime.strptime(date,'%d/%m/%Y')
    values = np.array(ls_values,ndmin = 2)
    pd_newEntry = pd.DataFrame(values,index = [dt_date], columns = ['volume','transaction','low','med','high','percPU'])
    
     
    #second we check if this company was already identified
    try:
        company_index = companies.index(company)
    except ValueError:
        companies.append(company)
        
        #well this is the first time we read in this company. lets add a new dictionary for it and then append it into the list of companies(ls_companies)
        #also certainly, since this is just new found it only has, so far, a single debt instrument                
        d_company = {'name': company, code : pd_newEntry}
        ls_companies.append(d_company)
        company_index = -1
        
        
        
        
    if company_index != -1: #that means we need to look in the correct list index, and check whether or not this debt instrument already exists
         #check if debt instrument already exists
        if debt_instrument in ls_companies[company_index].keys():
            ls_companies[company_index][debt_instrument] = ls_companies[company_index][debt_instrument].append(pd_newEntry)            
        else:
            ls_companies[company_index][debt_instrument] = pd_newEntry


#once all the data was loaded let's fill up daily
ls_liquid_companies = []
liquid_companies    = []

for idx_company,this_company in enumerate(ls_companies):
    for each_debt in this_company.keys():
        print each_debt
        if each_debt != 'name':
            this_company[each_debt] = this_company[each_debt].sort(ascending = True)
            
            #For a given debt instrument if there are less than 10 entries or the last trade was done in 2015 let's just ignore it!
            if this_company[each_debt].index.shape[0] > 10    and    this_company[each_debt].index[-1] > dt.datetime(2016,1,1):
                newtimeRange = pd.date_range(start = this_company[each_debt].index[0], end = this_company[each_debt].index[-1], freq = 'd')
                this_company[each_debt] = this_company[each_debt].reindex(index = newtimeRange, columns = ['volume','transaction','low','med','high','percPU'], method = 'pad')
            else:
               
                print 'Debt instrument: ' + each_debt + ' was deleted'
                this_company.pop(each_debt, None)
               
                
    
    #check if all debt instruments were deleted. if that's the case let's delete the whole company
#    if len(this_company.keys()) < 2:
#        print 'Company : '  + this_company['name'] +  ' was deleted due to either lack of data or securities that are not longer traded'
#        ls_companies.pop(idx_company)
#        companies.pop(idx_company)     
    if len(this_company.keys()) > 1:
        print 'Company : '  + this_company['name'] +  ' was added due since it is actively traded up to 2016'
        ls_liquid_companies.append(ls_companies[idx_company])
        liquid_companies.append(companies[idx_company])    
        
                
del ls_companies
ls_companies = copy.copy(ls_liquid_companies)                     
    
    
    
pickle.dump((ls_companies), open('debentures.p','wb'))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    