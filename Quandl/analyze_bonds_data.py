# -*- coding: utf-8 -*-
"""
Created on Mon Aug 08 11:22:28 2016

@author: vian
"""

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
from scipy import optimize
from xlrd import open_workbook
import pickle

from matplotlib.backends.backend_pdf import PdfPages

from re import sub
from decimal import Decimal
import math
import matplotlib.pyplot as plt
import copy

import datetime as dt
import dateutil



    
ls_companies     = pickle.load(open('debentures.p','rb'))
ls_termStructure = pickle.load(open('debentures_termStructure.p','rb'))
period = 30 #days   
    
 


def plot_termStructure(ls_termStructure):

    
       
    pp = PdfPages('companies/debentures_sortedByVolatility_debtWall.pdf')
    
    
    for aCompany in ls_termStructure:
        expiration_dates = []
        amount           = []
        ranking          = []
        coupon           = []
        fig = plt.figure()
        ax = plt.gca()
        
        for each_debt in aCompany.keys():
            if each_debt != 'name':
                expiration_dates.append(aCompany[each_debt]['expiration'])
                amount.append(aCompany[each_debt]['number_issued']*aCompany[each_debt]['price_issued'])
                            
                ranking.append(aCompany[each_debt]['ranking'])
                coupon.append(aCompany[each_debt]['interest'])
                
                #we are now painting each bar according to the securities ranking
                if ranking[-1] in 'Quirografria':
                    color_bar = '0.5'
                elif ranking[-1] in 'Subordinada':
                    color_bar = 'r'
                elif ranking[-1] in 'Flutuante':
                    color_bar = 'b'
                elif ranking[-1] in 'Real':
                    color_bar = 'g'
                    
                else:
                    color_bar = 'magenta'
                    
                ax.bar(expiration_dates[-1],amount[-1]/1e6, 40, color = color_bar)
                plt.text(expiration_dates[-1],1.02*amount[-1]/1e6,each_debt + ': ' + str(coupon[-1]) + '%')
                 
                
                
        
        dateLim = max(expiration_dates)
        plt.xlim((dt.datetime.today(),dt.datetime(dateLim.year + 1, dateLim.month, dateLim.day)))
        plt.ylim((ax.get_ylim()[0],ax.get_ylim()[1]*1.1))
        labels = ax.xaxis.get_ticklabels()
        plt.setp(labels,rotation = -30)
        plt.ylabel('Debt wall in  millions of BRL')
        plt.title(aCompany['name'])
        
        pp.savefig()       
            #plt.savefig('companies/' + sub('/','',aCompany['name'])+ '.png',dpi=50)
    pp.close()
    
#def plot_termStruct(ls_termStructure):
        
    
    
    
    
def plot_all_bonds(ls_companies, period = 30):

    pp = PdfPages('companies/debentures_sortedByVolatility.pdf')

    
    for aCompany_idx in range(len(ls_companies)):#len(companies)):
        aCompany = ls_companies[aCompany_idx]
        n_debtInstruments = len(aCompany.keys()) - 1
        
        f, axes = plt.subplots( nrows = n_debtInstruments, ncols = 3, sharex = True, figsize=(12, 8))
        f.suptitle(aCompany['name'])
        
        if n_debtInstruments == 1:
            axes = np.vstack(axes)
            axes = axes.T
        
        cntr = 0
        for each_debt in aCompany.keys():
            if each_debt != 'name':
                
                try:
                
                    axes[cntr,0].set_title(each_debt)
                    if all(pd.isnull(aCompany[each_debt]['percPU'])):
                        aCompany[each_debt][['med']].plot(ax = axes[cntr,0])
                    else:
                        aCompany[each_debt][['percPU']].plot(ax = axes[cntr,0]) 
                        axes[cntr,0].locator_params(nbins=2)
                        axes[cntr,0].legend().set_visible(False)
                        
                        
                        
                        aCompany[each_debt][['return7d']].plot(ax = axes[cntr,1])
                        axes[cntr,1].locator_params(nbins=2) 
                        axes[cntr,1].legend().set_visible(False)
                         
                         
                        axes[cntr,2].set_title(each_debt + ': volatility')
                        
                        aCompany[each_debt][['volatility']].plot(ax = axes[cntr,2])
                        axes[cntr,2].locator_params(nbins=2) 
                        axes[cntr,2].legend().set_visible(False)
                   
                        #del rollReturn, volatility
                    cntr = cntr + 1
                
                except ValueError:
                    cntr = cntr + 1
            
        del axes, f          
                 
                
        pp.savefig()       
        #plt.savefig('companies/' + sub('/','',aCompany['name'])+ '.png',dpi=50)
    pp.close()

    
    
def select_most_volatile(ls_companies, period = 30):
    ls_volatilities = []
    
    for aCompany_idx in range(len(ls_companies)):#len(companies)):
        aCompany = ls_companies[aCompany_idx]
        n_debtInstruments = len(aCompany.keys()) - 1   
        cntr = 0
        np_vol = np.zeros((1,n_debtInstruments))
        for each_debt in aCompany.keys():
            if each_debt != 'name':
                try:
                    #compute volatility using percPU or med
                    measure = 'percPU'
                    if all(pd.isnull(aCompany[each_debt]['percPU'])):
                        measure = 'med'
                    

                    rollReturn = aCompany[each_debt][measure]/aCompany[each_debt][measure].shift(1) - 1
                    aCompany[each_debt]['return7d'] = aCompany[each_debt][measure]/aCompany[each_debt][measure].shift(7) - 1
                    
                    aCompany[each_debt]['volatility'] = pd.rolling_std(rollReturn, window = period)*np.sqrt(period)
                    np_vol[0][cntr] = np.mean(aCompany[each_debt]['volatility'])
               
                    del rollReturn
                    cntr = cntr + 1
                
                except ValueError:
                    cntr = cntr + 1
        #aCompany['np_avg_vol'] = np.mean(np_vol)
        ls_volatilities.append(np.mean(np_vol))
        
        
        
    indx = np.argsort(ls_volatilities)    
    np_companies_sortedVol = np.array(ls_companies)[indx[::-1]]
    ls_companies = np_companies_sortedVol.tolist()
    
    pickle.dump(ls_companies, open('debentures.p','wb'))            
    return ls_companies




def compute_yield_to_maturity(ls_companies,ls_termStructure):
    DI = 0.1413
    IPCA = 0.08 
    
    start = 0
    ls_ytm = []
    ls_debt = []
    d_debt_ytm = {}
    company_idx = copy.copy(start)
    for aCompany in ls_companies:
        n_debtInstruments = len(aCompany.keys()) - 1   
        print aCompany['name'] + ' \n ====================='
        for each_debt in aCompany.keys():
            if each_debt != 'name':
                try:
                    #compute volatility using percPU or med
                    measure = 'percPU'
                    #if all(pd.isnull(aCompany[each_debt]['percPU'])):
                        #measure = 'med'
                    
                    #years to maturity! (accrued amount needs to be taken into account!)
                    T = ls_termStructure[company_idx][each_debt]['expiration'].year - aCompany[each_debt].index[-1].year
                    if ls_termStructure[company_idx][each_debt]['interest_reference'] == 'DI':
                        coupon = ls_termStructure[company_idx][each_debt]['interest'] + DI
                    elif ls_termStructure[company_idx][each_debt]['interest_reference'] == 'IPCA':
                        coupon = ls_termStructure[company_idx][each_debt]['interest'] + IPCA
                    else:
                        print each_debt + 'is neither wrt DI nor IPCA'
                        coupon = np.nan
                            
                    
                    if not np.isnan(coupon):
                        y0 = 0.15
                        price = aCompany[each_debt]['percPU'][-1]
                        ytm = optimize.newton(cash_flow_coupon,y0, args = (coupon,T,price))
                        print each_debt + 'YTM: ' +  str(ytm*100) + '%'
                        ls_debt.append(each_debt)
                        ls_ytm.append(ytm*100)
                    
                        
                    
               
                    
                    
                
                except ValueError:
                    print "Error at "  + each_debt
        
        company_idx = company_idx + 1
    
    idx = sorted(range(len(ls_ytm)),key = lambda k: ls_ytm[k], reverse = True)
    ls_ytm = sorted(ls_ytm, reverse = True)
    
    d_debt_ytm['debt'] = ls_debt
    d_debt_ytm['ytm']  = ls_ytm
    return d_debt_ytm

        


def cash_flow_coupon(y,coupon,T,price):
    t = np.linspace(0,T,T+1)
    return price - np.sum(coupon/(1.0+y)**t) - 100.0/(1.0 + y)**T
    





def get_debt_load(ls_companies):
    ls_termStructure = []

    for this_company in ls_companies:
        print this_company['name']
        d_termStruct = {}
        d_termStruct = {'name': this_company['name']}
        for each_debt in this_company.keys():
            if each_debt != 'name':
                
                #now we go to the ANBIMA website and get additional info there
                
                d_termStruct[each_debt] = scrap_debt_load(each_debt)
               
        ls_termStructure.append(d_termStruct)   
        
    pickle.dump(ls_termStructure, open('debentures_termStructure.p','wb')) 
    return ls_termStructure
           
                    
def scrap_debt_load(ticker = None, httpAddress = None ):
    if httpAddress is None:
        httpAddress = 'http://www.debentures.com.br/exploreosnd/consultaadados/emissoesdedebentures/caracteristicas_d.asp?tip_deb=publicas&selecao='
    
    if ticker is None:
        ticker = 'CMDT23'
        print 'A dummy will be loaded, namely ' + ticker
        
    print ticker   
    url = urllib2.urlopen(httpAddress + ticker)

    content = url.read()
    soup = BeautifulSoup(content)
    
    #get main table    
    mainTab = soup.find('table', {'class' : 'Tab10666666_2'})
    
    tableRows = mainTab.findAll('tr')
    cell      = tableRows[5].findAll('td')
    ranking = cell[2].findAll( text = True)[4][1:-1].encode('ascii','ignore')
    
    #lets clean up the garbage in the data
    ranking = re.sub(r"\s","",ranking)
    
    #get all the dates correctly!!
    expiration = tableRows[6].findAll(text = True)[10].encode('ascii', 'ignore')
    expiration = re.sub(r"\s","",expiration)
    try:
        expiration = dt.datetime.strptime(expiration, '%d/%m/%Y')
    except ValueError:
        print 'Expiration had the value of: ' + expiration + ' \n It will be set to a default value of 2010'
        expiration = dt.datetime(2010,1,1)
        
    
    emission   = tableRows[6].findAll(text = True)[6].encode('ascii', 'ignore') 
    emission   = re.sub(r"\s","",emission)
    emission   = dt.datetime.strptime(emission, '%d/%m/%Y')
    
    
    #lets now get how many debt was issued
    N_issued       = tableRows[7].findAll(text = True)[6].encode('ascii', 'ignore')
    N_issued      = re.sub(r"\s", "",N_issued)
    number_issued = float(re.sub(r'[^\d.]','',N_issued.translate(maketrans('.,',',.'))))
    
    #and of course, how much each debt sold for
    P_issued     = tableRows[8].findAll ( text = True)[6].encode('ascii', 'ignore')
    P_issued     = re.sub(r"\s", "",P_issued)
    price_issued = float(re.sub(r'[^\d.]','',P_issued.translate(maketrans('.,',',.'))))
    
    #amount issued
    debt_amount  = number_issued*price_issued
    
    
    interestTab = soup.find('table', {'class' : 'Tab10666666'})
    if interestTab is None:
        print 'Interest rate table was empty!'
        interest  = np.nan
        frequency = np.nan
        
    else:
        
        interest = interestTab.findAll(text = True)[5].encode('ascii', 'ignore')
        try:
            interest = float(re.sub(r'[^\d.]','',interest.translate(maketrans('.,',',.'))))
        except ValueError:
            print 'Interest is not a numeric value: ' + interest
            interest = np.nan
            
        frequency = interestTab.findAll(text = True)[12].encode('ascii', 'ignore')
    
    
    
    
    
    interest_base = tableRows[-1].findAll('td')
    interest_base = interest_base[2].findAll(text = True)[2].encode('ascii', 'ignore')
    interest_reference = re.sub(r"\s","", interest_base)
    

    
    debenture_info = dict(zip(['ranking','emission', 'expiration', 'number_issued', 'price_issued', 'debt_amount','interest', 'frequency','interest_reference'],[ranking,emission, expiration, number_issued, price_issued, debt_amount,interest, frequency, interest_reference]))
    return debenture_info    


            
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    