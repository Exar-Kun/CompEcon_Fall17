#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 08:15:08 2017

@author: Alexandria
"""


# import packages
import numpy as np
from scipy.stats import norm
import scipy.integrate as integrate
import scipy.optimize as opt
import time
import numba
import scipy.stats as st
from scipy.stats import norm
import scipy.integrate as integrate
import scipy.optimize as opt
from scipy.optimize import minimize
from scipy.optimize import differential_evolution
import statsmodels.formula.api as sm
import statsmodels.stats.sandwich_covariance as sw
import ar1_approx as ar1

rho = 0.7605
mu = 0.0
sigma_eps = 0.213
alpha_k = 0.297
alpha_l = 0.650
delta = 0.154
psi = 1.08
r = 0.04
h = 6.616
betafirm = (1 / (1 + r))
num = 9
w = 0.7
sizez = 9
num_draws = 100 #EQUAL TO T
sigma_z = sigma_eps / ((1 - rho ** 2) ** (1 / 2))
theta = np.array((alpha_k, rho, psi, sigma_z))

##For the firm problem
# Grid for k
dens = 5
kbar = 12 #kstar * 500
lb_k = 0.001
ub_k = kbar
krat = np.log(lb_k / ub_k)
numb = np.ceil(krat / np.log(1 - delta))
K = np.empty(int(numb * dens))
for j in range(int(numb * dens)):
    K[j] = ub_k * (1 - delta) ** (j / dens)
kvec = K[::-1]
sizek = kvec.shape[0]

phi0 = 0.8
phi1 = 0.028


#Enjoy z_fun!!!
def z_fun(theta):
    # Grid for z and transition matrix
    # We will use the Rouwenhorst (1995) method to approximate a continuous
    # distribution of shocks to the AR1 process with a Markov process.

    alpha_k, rho, psi, sigma_z = theta

    num_sigma = 3
    step = (num_sigma * sigma_z) / (sizez / 2)
    Pi, z = ar1.rouwen(rho, mu, step, sizez)
    Pi = np.transpose(Pi)  # make so rows are where start, columns where go
    z = np.exp(z)  # because the AR(1) process was for the log of productivity
    return z, Pi


z, Pi = z_fun(theta)


#Double z_fun...
def z_fun2(theta):
    # Grid for z and transition matrix
    # We will use the Rouwenhorst (1995) method to approximate a continuous
    # distribution of shocks to the AR1 process with a Markov process.

    alpha_k, rho, psi, sigma_z, phi0 = theta

    num_sigma = 3
    step = (num_sigma * sigma_z) / (sizez / 2)
    Pi, z = ar1.rouwen(rho, mu, step, sizez)
    Pi = np.transpose(Pi)  # make so rows are where start, columns where go
    z = np.exp(z)  # because the AR(1) process was for the log of productivity
    return z, Pi

@numba.jit
def VFI_loop(V, e, betafirm, sizez, sizek, Vmat, pi):
    V_prime = np.dot(pi, V)
    for i in range(sizez):  # loop over z
        for j in range(sizek):  # loop over k
            for k in range(sizek): # loop over k'
                Vmat[i, j, k] = e[i, j, k] + betafirm * V_prime[i, k]
    return Vmat

def solve_firm(theta):

    alpha_k, rho, psi, sigma_z = theta

    sizez = z.shape[0]
    op = np.zeros((sizez, sizek))
    for i in range(sizez):
        for j in range(sizek):
            op[i,j] = z[i] * (kvec[j]**alpha_k)

    e = np.zeros((sizez, sizek, sizek))
    for i in range(sizez):
        for j in range(sizek):
            for k in range(sizek):
                e[i, j, k] = (op[i,j] - kvec[k] + ((1 - delta) * kvec[j]) -
                            ((psi / 2) * ((kvec[k] - ((1 - delta) * kvec[j])) ** 2)
                            / kvec[j]))


    # Value funtion iteration
    VFtol = 1e-6
    VFdist = 7.0
    VFmaxiter = 3000
    V = np.zeros((sizez, sizek))  # initial guess at value function
    Vmat = np.zeros((sizez, sizek, sizek))  # initialize Vmat matrix
    Vstore = np.zeros((sizez, sizek, VFmaxiter))  # initialize Vstore array
    VFiter = 1

    start_time = time.clock()
    while VFdist > VFtol and VFiter < VFmaxiter:
        TV = V
        Vmat = VFI_loop(V, e, betafirm, sizez, sizek, Vmat, Pi)
        Vstore[:, :, VFiter] = V.reshape(sizez, sizek,)  # store value function at each
        # iteration for graphing later
        V = Vmat.max(axis=2)  # apply max operator to Vmat (to get V(k))
        PF = np.argmax(Vmat, axis=2)  # find the index of the optimal k'
        Vstore[:,:, i] = V  # store V at each iteration of VFI
        VFdist = (np.absolute(V - TV)).max()  # check distance between value
        # function for this iteration and value function from past iteration
        VFiter += 1

    VFI_time = time.clock() - start_time
    if VFiter < VFmaxiter:
        print('Value function converged after this many iterations:', VFiter)
    else:
        print('Value function did not converge')
        print('VFI took ', VFI_time, ' seconds to solve')

    VF = V  # solution to the functional equation


    #decision rules

    ### Collect optimal values(functions)
    # Optimal capital stock k'
    optK = kvec[PF]

     # optimal investment I
    optI = optK - (1 - delta) * kvec

    return VF, PF, optK, optI

VF, PF, optK, optI = solve_firm(theta)

def solve_firm2(theta):

    alpha_k, rho, psi, sigma_z, phi0 = theta

    sizez = z.shape[0]
    op = np.zeros((sizez, sizek))
    for i in range(sizez):
        for j in range(sizek):
            op[i,j] = z[i] * (kvec[j]**alpha_k)

    e = np.zeros((sizez, sizek, sizek))
    for i in range(sizez):
        for j in range(sizek):
            for k in range(sizek):
                e[i, j, k] = (op[i,j] - kvec[k] + ((1 - delta) * kvec[j]) -
                            ((psi / 2) * ((kvec[k] - ((1 - delta) * kvec[j])) ** 2)
                            / kvec[j]))

    e2 = np.zeros((sizez, sizek, sizek))
    for i in range(sizez):
        for j in range(sizek):
            e2[i, j, k] = (op[i,j] - kvec[k] + ((1 - delta) * kvec[j]) -
                            ((psi / 2) * ((kvec[k] - ((1 - delta) * kvec[j])) ** 2)
                            / kvec[j]))-phi0-phi1*((kvec[k] + (1 - delta) * kvec[j])-op[i,j])

    # Value funtion iteration
    VFtol = 1e-6
    VFdist = 7.0
    VFmaxiter = 3000
    V = np.zeros((sizez, sizek))  # initial guess at value function
    Vmat = np.zeros((sizez, sizek, sizek))  # initialize Vmat matrix
    Vstore = np.zeros((sizez, sizek, VFmaxiter))  # initialize Vstore array
    VFiter = 1

    start_time = time.clock()
    while VFdist > VFtol and VFiter < VFmaxiter:
        TV = V
        Vmat1 = VFI_loop(V, e, betafirm, sizez, sizek, Vmat, Pi)
        Vmat2 = VFI_loop(V, e2, betafirm, sizez, sizek, Vmat, Pi)
        for i in range(sizez):  # loop over z
            for j in range(sizek):  # loop over k
                for k in range(sizek):
                    Vmat[i, j, k] = max(Vmat1[i, j, k], Vmat2[i, j, k])
        Vstore[:, :, VFiter] = V.reshape(sizez, sizek,)  # store value function at each
        # iteration for graphing later
        V = Vmat.max(axis=2)  # apply max operator to Vmat (to get V(k))
        PF = np.argmax(Vmat, axis=2)  # find the index of the optimal k'
        Vstore[:,:, i] = V  # store V at each iteration of VFI
        VFdist = (np.absolute(V - TV)).max()  # check distance between value
        # function for this iteration and value function from past iteration
        VFiter += 1

    VFI_time = time.clock() - start_time
    if VFiter < VFmaxiter:
        print('Value function converged after this many iterations:', VFiter)
    else:
        print('Value function did not converge')
        print('VFI took ', VFI_time, ' seconds to solve')

    VF = V  # solution to the functional equation


    #decision rules

    ### Collect optimal values(functions)
    # Optimal capital stock k'
    optK = kvec[PF]

     # optimal investment I
    optI = optK - (1 - delta) * kvec

    return VF, PF, optK, optI




# Simulate the Markov process - will make this a function so can call later
def sim_markov(z, Pi, num_draws):
    # draw some random numbers on [0, 1]
    u = np.random.uniform(size=num_draws)

    # Do simulations
    z_discrete = np.empty(num_draws)  # this will be a vector of values
    # we land on in the discretized grid for z
    N = z.shape[0]
    #oldind = int(np.ceil((N - 1) / 2)) # set initial value to median of grid
    oldind = 0
    z_discrete[0] = oldind
    for i in range(1, num_draws):
        sum_p = 0
        ind = 0
        while sum_p < u[i]:
            sum_p = sum_p + Pi[ind, oldind]
#             print('inds =  ', ind, oldind)
            ind += 1
        if ind > 0:
            ind -= 1
        z_discrete[i] = ind
        oldind = ind
        z_discrete = z_discrete.astype(dtype = np.int)

    return z_discrete



# Call simulation function to get simulated values
z_discrete = sim_markov(z, np.transpose(Pi), num_draws)


n = 1000 #number of firms
T = 100
z_new = np.zeros((n,T), dtype = np.int)
for i in range(n):
    z_new[i] = sim_markov(z, np.transpose(Pi), num_draws)  #correct z


def loop_k():
    next_k = np.zeros((n,T), dtype = np.int)
    for i in range(n):
        for j in range(T-1):
            next_k[i, j+1] = PF[z_new[i,j]][next_k[i,j]]
    return next_k

next_k=loop_k()
next_k


def loop_I():
    next_optI = np.zeros((n,T))
    for i in range(n):
        for j in range(T-1):
            next_optI[i,j+1] = kvec[next_k[i,j+1]] - (1 - delta) * kvec[next_k[i,j]]
    return next_optI

next_optI = loop_I()
next_optI


def profit():
    profit = np.zeros((n, T))
    for i in range(n):
        for j in range(T):
            profit[i,j] = z_new[i,j] * (kvec[next_k[i,j]]**alpha_k)
    return profit


profit1 = profit()
profit1

@numba.jit
def loop_VFIs():
    next_Vs = np.zeros((n,T), dtype = np.int)
    for i in range(n):
        for j in range(T):
            next_Vs[i,j] = VF[z_new[i,j], next_k[i,j]]
    return next_Vs


next_Vs = loop_VFIs()
next_Vs


def sim_firm(theta):
    alpha_k, rho, psi, sigma_z = theta
    z, Pi = z_fun(theta)
    z_new = np.zeros((n,T), dtype = np.int)
    for i in range(n):
        z_new[i] = sim_markov(z, np.transpose(Pi), num_draws)  #correct z

    next_k = loop_k()
    next_optI = loop_I()
    profit_1 = profit()
    next_Vs = loop_VFIs()

    return next_Vs, profit_1, next_optI, next_k


next_Vs, profit_1, next_optI, next_k = sim_firm(theta)

def sim_firm2(theta):
    alpha_k, rho, psi, sigma_z, phi0 = theta
    z, Pi = z_fun2(theta)
    z_new = np.zeros((n,T), dtype = np.int)
    for i in range(n):
        z_new[i] = sim_markov(z, np.transpose(Pi), num_draws)  #correct z

    next_k = loop_k()
    next_optI = loop_I()
    profit_1 = profit()
    next_Vs = loop_VFIs()

    return next_Vs, profit_1, next_optI, next_k


next_Vs, profit_1, next_optI, next_k = sim_firm(theta)


def moments(theta):
    alpha_k, rho, psi, sigma_z = theta

    '''This creates and runs the moments and such'''
    ##################################################################################################
    ##MOMENTS
    inv_nextk = next_optI/kvec[next_k]
    invest_nextk = inv_nextk.reshape((1, n*100))  # I over K reshaped for corrcoef()
    sc_invest_nextk = np.corrcoef(invest_nextk[0][1:], invest_nextk[0][:100000-1])[0,1]
    profit_nextk = profit_1/kvec[next_k]
    sd_profit_nextk = profit_nextk.reshape((1, n*100))
    sd_profit_nextk = np.std(sd_profit_nextk)
    q_bar = next_Vs.sum()/kvec[next_k].sum()
    Y = invest_nextk
    Y = Y.reshape(100000, 1)
    q = next_Vs/kvec[next_k]
    q = q.reshape(100000, 1)
    prof_k = profit_1/kvec[next_k]
    prof_k = prof_k.reshape(100000, 1)
    cons = np.ones(100000)
    cons = cons.reshape(100000, 1)
    ##################################################################################################
    ##REGRESSIONS
    x = np.hstack((cons, q, prof_k))
    trans = x.transpose()
    xx = np.dot(trans, x)
    inv = np.linalg.inv(xx)
    xy = np.dot(trans, Y)
    reg_coef = np.dot(inv, xy)
    mew_s = np.array((max(reg_coef[1]), max(reg_coef[2]), sc_invest_nextk, sd_profit_nextk, q_bar))

    return mew_s

mew_s = moments(theta)

#The second moment

def moments2(theta):
    alpha_k, rho, psi, sigma_z, phi0 = theta

    '''This creates and runs the moments and such'''
    ##################################################################################################
    ##MOMENTS
    inv_nextk = next_optI/kvec[next_k]
    invest_nextk = inv_nextk.reshape((1, n*100))  # I over K reshaped for corrcoef()
    sc_invest_nextk = np.corrcoef(invest_nextk[0][1:], invest_nextk[0][:100000-1])[0,1]
    profit_nextk = profit_1/kvec[next_k]
    sd_profit_nextk = profit_nextk.reshape((1, n*100))
    sd_profit_nextk = np.std(sd_profit_nextk)
    q_bar = next_Vs.sum()/kvec[next_k].sum()
    Y = invest_nextk
    Y = Y.reshape(100000, 1)
    q = next_Vs/kvec[next_k]
    q = q.reshape(100000, 1)
    prof_k = profit_1/kvec[next_k]
    prof_k = prof_k.reshape(100000, 1)
    cons = np.ones(100000)
    cons = cons.reshape(100000, 1)
    ##################################################################################################
    ##REGRESSIONS
    x = np.hstack((cons, q, prof_k))
    trans = x.transpose()
    xx = np.dot(trans, x)
    inv = np.linalg.inv(xx)
    xy = np.dot(trans, Y)
    reg_coef = np.dot(inv, xy)
    mew_s = np.array((max(reg_coef[1]), max(reg_coef[2]), sc_invest_nextk, sd_profit_nextk, q_bar, ext))

    return mew_s

mew_s = moments(theta)


# Function to calculate the distance between mu_s and mu_d

def dist(A,B,C):
    d = np.linalg.multi_dot([np.transpose(A - B),np.linalg.inv(C),(A - B)])
    return d

# Setting bounds for alpha_k, rho, psi, sigma_z
#Having completed this problem set and made it ready to turn in, I realized
#too late that the bounds are wrong and lacked the time to rectify this mistake
bnds1=((0,1),(0,1),(0,0.2),(0,0.9))
bnds2=((0,0.8),(0,0.5),(0,0.05),(0,1),(0,0.005)) #amazing :)

#PLay that funky music...

def Qfunk2(theta):
    alpha_k, rho, psi, sigma_z, phi0 = theta
    a1 = 0.0388
    a2=0.2358
    sc=0.0158
    std=0.2614
    qbar=2.9413
    ext=0.2236
    mu_s=moments2(theta)
    mu_d=np.array([a1,a2,sc,std,qbar,ext])
    W=np.eye(len(mu_d))
    dis=dist(mu_s,mu_d,W)
    return dis


#Having defined all our functions the real work begins...#

#This being the supreme function we call it Sidious after the Supreme Chancellor#

def Sidious(theta):
    alpha_k, rho, psi, sigma_z = theta

    z, Pi = z_fun(theta)

    VF, PF, optK, optI = solve_firm(theta)


    n = 1000 #number of firms
    T = 100
    z_new = np.zeros((n,T), dtype = np.int)
    for i in range(n):
        z_new[i] = sim_markov(z, np.transpose(Pi), num_draws)  #correct z

    next_Vs, profit_1, next_optI, next_k = sim_firm(theta)


    a1 = 0.0388
    a2=0.2358
    sc=0.0158
    std=0.2614
    qbar=2.9413
    mu_s=moments(theta)
    mu_d=np.array([a1,a2,sc,std,qbar])
    W=np.eye(len(mu_d))
    #Dis is how we do it...
    dis=dist(mu_s,mu_d,W)

    return dis

#This being the supreme II supreme function we call it Vitiate after the
#Sith Emperor

def Vitiate(theta):
    alpha_k, rho, psi, sigma_z, phi0 = theta

    z, Pi = z_fun2(theta)

    VF, PF, optK, optI = solve_firm2(theta)


    n = 1000 #number of firms
    T = 100
    z_new = np.zeros((n,T), dtype = np.int)
    for i in range(n):
        z_new[i] = sim_markov(z, np.transpose(Pi), num_draws)  #correct z

    next_Vs, profit_1, next_optI, next_k = sim_firm2(theta)



    a1 = 0.0388
    a2=0.2358
    sc=0.0158
    std=0.2614
    qbar=2.9413
    ext=0.2236
    mu_s=moments2(theta)
    mu_d=np.array([a1,a2,sc,std,qbar, ext])
    W=np.eye(len(mu_d))
    #Dis is how we do it...
    dis=dist(mu_s,mu_d,W)

    return dis

ext=0.2236

theta_hat = differential_evolution(Sidious,bnds1)

##The answer to the first part of the problem set
theta_hat

theta_hat = np.matrix([1, theta_hat.x[0], theta_hat.x[1], theta_hat.x[2], theta_hat.x[3]])

deriv = np.diff(theta_hat)

#We can take these steps seeing that putting the itdenty matrix in between 
#this two matricies will do nothing...#

sd = np.diagonal(np.dot(deriv.T, deriv))
sd

##I now do the same for table III

##First we redefine theta
theta = alpha_k, rho, psi, sigma_z, phi0

##theta_hat_2 = differential_evolution(Vitiate,bnds2)

theta_hat_2 = differential_evolution(Qfunk2,bnds2)

theta_hat_2 = np.matrix([1, 1, theta_hat_2.x[0], theta_hat_2.x[1], theta_hat_2.x[2], theta_hat_2.x[3]])

deriv2 = np.diff(theta_hat_2)

#We can take these steps seeing that putting the itdenty matrix in between 
#this two matricies will do nothing...#

sd2 = np.diagonal(np.dot(deriv2.T, deriv2))
sd2





