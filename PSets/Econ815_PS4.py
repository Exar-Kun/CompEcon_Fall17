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

#We now divide this data by year lest we have horrible trouble with the
#creation of counterfactuals
data2007 = data[(data['year']==2007)] 

data2008 = data[(data['year']==2008)]

#Upon the generation of the counterfactuals we will use this to create
#distance data

##############################################################################
#########################Creating Counterfactuals#############################
##############################################################################

#We begin by finding all the values for the buyers 

for i in range(1, 45):
    cfi = data2007[(data['buyer_id']!= i)]
    cfi.drop('buyer_id', axis=1)
    cfi['buyer_id'] = i



    


##############################################################################
####################################Distance Data#############################
##############################################################################
