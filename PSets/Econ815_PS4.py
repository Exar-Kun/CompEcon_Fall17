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

##############################################################################
####################################Population Fixes##########################
##############################################################################

#Having done this we now turn to the fixing of the population variable so that
#it will produce better estimates for the parameters. The fix we propose is a 
#division of the variable into tens of thousands of people...
data['population'] = (data['population_target'] / 100000)

#We now test to see if this has been correctly done
max(data['population'].values.tolist())



#We now divide this data by year lest we have horrible trouble with the
#creation of counterfactuals
data2007 = data[(data['year']==2007)] 

data2008 = data[(data['year']==2008)]


data2007b = data2007[['buyer_id','num_stations_buyer', 'corp_owner_buyer', 
                      'buyer_coordinates', 'price']]
data2007t = data2007[['target_id','hhi_target', 'population', 
                      'target_coordinates', 'year']]

data2008b = data2008[['buyer_id','num_stations_buyer', 'corp_owner_buyer', 
                      'buyer_coordinates', 'price']]
data2008t = data2008[['target_id','hhi_target', 'population', 
                      'target_coordinates', 'year']]

#Upon the generation of the counterfactuals we will use this to create
#distance data

##############################################################################
#########################Creating Counterfactuals#############################
##############################################################################

#We begin by finding all the values for the buyers 

#To do this we must first create a blank dataframe
counter = pd.DataFrame()


for el in [[data2007b, data2007t], [data2008b, data2008t]]:
    for i in range(len(el[0])):
        for j in range(len(el[1])):
            if i != j:
                counter = counter.append(pd.concat(
                        [el[0].iloc[[i]].reset_index(drop=True), 
                         el[1].iloc[[j]].reset_index(drop=True)], axis=1))


#This being completed we reindex the dataframes 
counter = counter.reset_index(drop=True)

#A trial of the index
counter.buyer_coordinates[0]

##############################################################################
####################################Distance Data#############################
##############################################################################


#The data now being generated we move on to the creation of distance data
#We turn to a list comprehension to create this column as it is faster
#we are also unable to do so otherwise because of the idiosyncracies of the
#sara as well...

data['distance'] = [vincenty(data.buyer_coordinates.iloc[i], 
                                  data.target_coordinates.iloc[i]).miles 
                                    for i in range(len(data))]

#We now create the distances for the counterfactuals
counter['distance'] = [vincenty(counter.buyer_coordinates.iloc[i], 
                                  counter.target_coordinates.iloc[i]).miles 
                                    for i in range(len(counter))]

#We now print the data to ensure that we are doing things rightly
data.head(n=3)

#We do the same for the counterfactuals
counter.head(n=3)


##############################################################################
##########################Prepaperation for Maximization######################
##############################################################################
#We now cut the data set into pieces by year and counterfactuals vs matches

#Matches
match2007 = data[(data['year'] == 2007)]
match2008 = data[(data['year'] == 2008)]

#Counterfactuals
counter2007 = counter[(counter['year'] == 2007)]
counter2008 = counter[(counter['year'] == 2008)]

##############################################################################
##########################The Max Score Estimator#############################
##############################################################################

#We now turn to the creation of matrices by a list comphrehension in order to
#estimate the score function
    #Having spoken with my classmates it is well acknowledged that this is the 
    #fastest method to do these things.

#Here we create the payoff vector for the matches in 2007

def matpayoff2007(a, B):
    matches = [(match2007['num_stations_buyer'][i] * match2007['population'][i] + 
              a * match2007['corp_owner_buyer'][i] * match2007['population'][i]
              + B * match2007['distance'][i]) for i in range(len(match2007))]
    return(np.matrix(matches))
    
#We now create the match payoff vector for 2008
    
def matpayoff2008(a, B):
    matches = [(match2008['num_stations_buyer'][i] * match2008['population'][i] + 
              a * match2008['corp_owner_buyer'][i] * match2008['population'][i]
              + B * match2008['distance'][i]) for i in range(len(match2008))]
    return(np.matrix(matches))

#We now begin the creation of the two payoff matrices for the counterfactuals:
#one for each year

def matcounter2007(a, B):
    matches = [(counter2007['num_stations_buyer'][i] * counter2007['population'][i] + 
              a * counter2007['corp_owner_buyer'][i] * counter2007['population'][i]
              + B * counter2007['distance'][i]) for i in range(len(match2007))]
    return(np.matrix(matches))

#Finally having done this for 2007 we do it for 2008

def matcounter2008(a, B):
    matches = [(counter2008['num_stations_buyer'][i] * counter2008['population'][i] + 
              a * counter2008['corp_owner_buyer'][i] * counter2008['population'][i]
              + B * counter2008['distance'][i]) for i in range(len(match2008))]
    return(np.matrix(matches))

#Having defined the functions, we now create the specific objects
matches = matpayoff2007(1,1)

counter = matcounter2007(1, 1)

#We now begin to create the score function for 2007
def maxscr(b3):
    a, B = b3
    score = 0
    x = matpayoff2007(a, B)
    y = matcounter2007(a, B)
    y = y.reshape(47, 46)
    for i in range(len(x)):
        for j in range(len(x)):
            if j > i:
                if (x.item(i) + x.item(i+1) >= y.item(i, j-1) + y.item(j, i)):
                    score = score + 1
                 
    return score * -1
        
#We now optimize the score function
#As we have a discontinuous function we again use Nelder-Mead to optimize it

b3 = np.array((1, 1))

results = opt.minimize(maxscr, b3, method = 'Nelder-Mead', options={'disp': True})

print(results)

##############################################################################
##########################Additions to the Model##############################
##############################################################################


def fullmatpayoff2007(d, a, g, B):
    matches = [d * (match2007['num_stations_buyer'][i] * match2007['population'][i] + 
              a * match2007['corp_owner_buyer'][i] * match2007['population'][i]
              + g * match2007['hhi_target'][i]
              + B * match2007['distance'][i]) for i in range(len(match2007))]
    return(np.matrix(matches))
    
#We now create the match payoff vector for 2008
    
def fullmatpayoff2008(d, a, g, B):
    matches = [d * (match2008['num_stations_buyer'][i] * match2008['population'][i] + 
              a * match2008['corp_owner_buyer'][i] * match2008['population'][i]
              + g * match2008['hhi_target'][i]
              + B * match2008['distance'][i]) for i in range(len(match2008))]
    return(np.matrix(matches))

#We now begin the creation of the two payoff matrices for the counterfactuals:
#one for each year

def fullmatcounter2007(d, a, g, B):
    matches = [d * (counter2007['num_stations_buyer'][i] * counter2007['population'][i] + 
              a * counter2007['corp_owner_buyer'][i] * counter2007['population'][i]
              + g * counter2007['hhi_target'][i]
              + B * counter2007['distance'][i]) for i in range(len(counter2007))]
    return(np.matrix(matches))

#Finally having done this for 2007 we do it for 2008


def fullmatcounter2008(d, a, g, B):
    matches = [d * (counter2008['num_stations_buyer'][i] * counter2008['population'][i] + 
              a * counter2008['corp_owner_buyer'][i] * counter2008['population'][i]
              + g * counter2008['hhi_target'][i]
              + B * counter2008['distance'][i]) for i in range(len(counter2008))]
    return(np.matrix(matches))

#Having defined the functions, we now create the specific objects
matches = fullmatpayoff2007(1,1)

counter = fullmatcounter2007(1, 1)



#We now begin to create the score function for 2007
def maxscr2008(b3):
    a, B = b3
    score = 0
    x = matpayoff2008(a, B)
    y = matcounter2008(a, B)
    y = y.reshape(47, 46)
    for i in range(len(x)):
        for j in range(len(x)):
            if j > i:
                if (x.item(i) + x.item(i+1) >= y.item(i, j-1) + y.item(j, i)):
                    score = score + 1
                 
    return score * -1


#We now optimize the score function
#As we have a discontinuous function we again use Nelder-Mead to optimize it

results = opt.minimize(maxscr2008, b3, method='Nelder-Mead')

print(results)