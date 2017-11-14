#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 13:20:09 2017

@author: Alexandria
"""
# import packages
from pyjstat import pyjstat
import matplotlib
import matplotlib.pyplot as plt

#Here we make strings necessary to "tie up" our request
url = "http://ec.europa.eu/eurostat/wdds/rest/data/v2.1/json/en/"

data = "nama_gdp_c?precision=4&unit=EUR_HAB&shortLabel=1"

#I strap up my laces when I tie my shoes...
pull_request = url + data

# We now pull down the data...
dataset = pyjstat.Dataset.read(pull_request)

#Having pulled such data, we now write it unto a dataframe
data = dataset.write('dataframe')
data.head(n=3)

#This being done we now drop missing values (no value for trade flows)
data = data[data["value"].isnull() !=True]
data.head(n=3)

#We now cast out unnecessary indicators
data = data[data["indic_na"]=="Gross domestic product at market prices"]

#We now cut the data for a single country of Spain
Spain = data[data["geo"]=="Spain"]

#From thence we seek to graph the change in trade flows for several countries
#a simple visualization
% matplotlib inline

#We now prepare to do our line graph
Spain = Spain.set_index("time")
summary = Spain["value"].plot(kind="line")

# Formatting options
plt.style.use('fivethirtyeight')
plt.title('Spain GDP') # plot title, axis labels

#Finally we save the graph 
plt.savefig("ESP_GDP.png")


