#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 20:58:31 2017

@author: soumyadipghosh
"""
import numpy as np
import sys
from tkinter import *

n_b = 10
n_s = 10

#Load mean and sigma
load_mu , load_sigma = 100,30

loads_b = np.random.normal(load_mu,load_sigma,n_b)

#c mean and sigma
cb_mu,cb_sigma = 30, 10

#d mean and sigma
db_mu,db_sigma = 0.1 , 0.05

#Seller xs and sigma
xs_mu ,xs_sigma = 10, 5

ys_mu,ys_sigma = 0.1,0.05

import sys
from PyQt5 import QtWidgets, uic
 
qtCreatorFile = "energy_auction_simul.ui"
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('energy_auction_simul.ui', self)
        self.initUI()
        self.show()
 
    def initUI(self):
        self.setWindowTitle("Energy Auction Simulator")
        self.n_b.setText("10")
        self.n_s.setText("10")
        self.load_mu.setText("100")
        self.load_sigma.setText("30")
        self.cb_mean.setText("30")
        self.cb_sigma.setText("10")
        self.db_mean.setText("0.1")
        self.db_sigma.setText("0.05")
        self.xs_mean.setText("10")
        self.xs_sigma.setText("5")
        self.ys_mean.setText("0.1")
        self.ys_sigma.setText("0.05")


        self.run_auc.clicked.connect(self.buttonClicked) 
        
    
    def buttonClicked(self):
        
        n_b = self.n_b.text()
        n_s = self.n_s.text()
        load_mean = self.load_mu.text()
        load_sigma = self.load_sigma.text()
        cb_mean = self.cb_mean.text()
        cb_sigma = self.cb_sigma.text()
        db_mean = self.db_mean.text()
        db_sigma = self.db_sigma.text()
        xs_mean = self.xs_mean.text()
        xs_sigma = self.xs_sigma.text()
        ys_mean = self.ys_mean.text()
        ys_sigma = self.ys_sigma.text()
        price_func = self.price_combo.currentText()
        alpha_t = self.alpha_text.text()
        beta_t = self.beta_text.text()
        
        self.results.append("Running Energy Auction Simulation.")
        self.results.append("Buyers:" + n_b)
        self.results.append("Sellers:" + n_s)
        self.results.append("Price Aggregration:" + price_func)
        self.results.append("Alpha:" + alpha_t)
        
        self.simul(n_b,n_s,load_mean,load_sigma,cb_mean,cb_sigma,db_mean,db_sigma,xs_mean,xs_sigma,ys_mean,ys_sigma,price_func,alpha_t,beta_t)
        #QtWidgets.QMessageBox.about(self, "Title", n_b)
    
    def simul(self,n_b,n_s,load_mean,load_sigma,cb_mean,cb_sigma,db_mean,db_sigma,xs_mean,xs_sigma,ys_mean,ys_sigma,price_func,alpha_t,beta_t):
        
        prices = np.zeros(int(n_b))
        quants_b = np.random.normal(float(load_mean),float(load_sigma),int(n_b))
        self.results.append("Buyer Loads:" + str(quants_b))
        cb_arr = np.random.normal(float(cb_mean),float(cb_sigma),int(n_b))
        db_arr = np.random.normal(float(db_mean),float(db_sigma),int(n_b))
    
        for i in range(0,int(n_b)):
            prices[i] = abs(cb_arr[i] - db_arr[i]*quants_b[i])
                        
        market_price = self.price_agg(prices,quants_b,price_func)
        
        self.results.append("Initial Buyer Prices:" + str(prices))
        self.results.append("Initial Market Price:" + str(market_price))
        
        quants_s = np.zeros(int(n_s))
        xs_arr = np.random.normal(float(xs_mean),float(xs_sigma),int(n_s))
        ys_arr = np.random.normal(float(ys_mean),float(ys_sigma),int(n_s))
        
        for i in range(0,int(n_s)):
            quants_s[i] = (market_price - xs_arr[i])/ys_arr[i]
        quants_s[quants_s < 0] = 0
        
        while(np.sum(quants_b) > np.sum(quants_s)):
            
            quants_s = self.quant_upd_seller(quants_s,beta_t)
            
            quants_s[quants_s < 0] = 0
            
            prices = self.price_upd_buyer(prices,market_price,alpha_t)
            market_price = self.price_agg(prices,quants_b,price_func)
            QtWidgets.QMessageBox.about(self, "Prices", str(prices) + "Prices")
        
        self.results.append("Final Buyer Prices:" + str(prices))
        self.results.append("Final Market Price:" + str(market_price))
        self.results.append("Seller Quantities:" + str(quants_s))
        
    def price_upd_buyer(self,prices,market_price,alpha_t):
        
        alpha = float(alpha_t)
        for i in range(0,len(prices)):
            prices[i] = prices[i] + alpha*(market_price - prices[i])/prices[i] 

        return prices
    
    def quant_upd_seller(self,quants_s,beta_t):
        
        beta = float(beta_t)
        mean_quant = np.mean(np.array(quants_s))
        for i in range(0,len(quants_s)):
            if(quants_s[i] > 0):
                quants_s[i] = quants_s[i] + beta*(mean_quant - quants_s[i])/quants_s[i] 

        return quants_s

    def price_agg(self,prices,quants_b,price_func):
        
        mp = 0
        if(price_func == "Min"):
            mp = np.min(prices) #Minimum price
        elif(price_func == "Max"):
            mp = np.max(prices) #Maximum price
        elif(price_func == "Average"):
            mp = np.average(prices) #Average price
        elif(price_func == "Weighted Average by Quantity"):
            mp = np.average(prices,weights = quants_b) #Weighted Average
        elif(price_func == "Median"):
            mp = np.median(prices) #Median price
        elif(price_func == "75 Percentile"):
            mp = np.percentile(prices,75) # 75 quartile
        else:
            mp = np.average(np.sort(prices),weights = np.sort(quants_b)) #max quantities with max prices
        
        return mp

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater) # if using IPython Console
    window = Ui()
    sys.exit(app.exec_())
    


