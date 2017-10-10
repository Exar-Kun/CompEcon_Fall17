#Here begins the creation of a max score estimator in accordance with the
#guidelines set forth in Problem Set 4.

#We begin by importing the vast litany of packages that we will use
import pandas as pd
import numpy as np
import scipy.optimize as opt
from scipy.optimize import minimize
import scipy.stats as stats
import time
import math
from statsmodels.iolib.summary2 import summary_col
from geopy.distance import vincenty

##############################################################################
#########################Reading In The Data and Preliminaries################
##############################################################################

#Now we read in the data
data=pd.read_excel('radio_merger_data.xlsx')

#Having read in the data we now ensure it entered properly
data.head(n=3)

#Now we find the distance between buyers and targets
#Seeing that the vincenty function will only take tuples, we must combine
#the longitude and latitude columns for buyers and sellers.
data['buyer_coordinates'] = list(zip(data.buyer_lat, data.buyer_long))

data.head(n=3)

#Having attained the proper result for the buyer coordinates, we now do the 
#smae for the target coordinates
data['target_coordinates'] = list(zip(data.target_lat, data.target_long))

data.head(n=3)

#We now drop the longitude and latitude columns as we now have full cordinate
#columns.
data = data[['buyer_id','num_stations_buyer', 'corp_owner_buyer', 
             'buyer_coordinates', 'target_id','hhi_target', 'price', 
             'population_target', 'target_coordinates', 'year']]

#We now divide this data by year lest we have horrible trouble with the
#creation of counterfactuals
data2007 = data[(data['year']==2007)] 

data2008 = data[(data['year']==2008)]


data2007b = data2007[['buyer_id','num_stations_buyer', 'corp_owner_buyer', 
                      'buyer_coordinates', 'price']]
data2007t = data2007[['target_id','hhi_target', 'population_target', 
                      'target_coordinates', 'year']]

data2008b = data2008[['buyer_id','num_stations_buyer', 'corp_owner_buyer', 
                      'buyer_coordinates', 'price']]
data2008t = data2008[['target_id','hhi_target', 'population_target', 
                      'target_coordinates', 'year']]

#Upon the generation of the counterfactuals we will use this to create
#distance data

##############################################################################
#########################Creating Counterfactuals#############################
##############################################################################

#We begin by finding all the values for the buyers 

counter = pd.DataFrame()

for i in range(len(data2007b)):
    for j in range(len(data2007t)):
        if i != j:
            counter = counter.append(pd.concat(
                    [data2007b.iloc[[i]].reset_index(drop=True), 
                    data2007t.iloc[[j]].reset_index(drop=True)], axis=1))

#Having now created the data we seek, we combine it with the initial dataframe
full_data = pd.concat([data, counter])

#This being completed we reindex the dataframe 
full_data = full_data.reset_index(drop=True)

#A trial of the index
full_data.buyer_coordinates[0]

##############################################################################
####################################Distance Data#############################
##############################################################################


#The data now being generated we move on to the creation of distance data
full_data['distance'] = [vincenty(full_data.buyer_coordinates.iloc[i], 
                                  full_data.target_coordinates.iloc[i]).miles 
                                    for i in range(len(full_data))]

#We now print the data to ensure that we are doing things rightly
full_data.head(n=3)

##############################################################################
##########################The Max Score Estimator#############################
##############################################################################

#Finally, having produced the relevant data, we move on to the creation of 
#the max score estimator


