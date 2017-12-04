#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 08:18:36 2017

@author: Alexandria
"""

def main(V, e, betafirm, sizez, sizek, Vmat, pi):

    # Define a function of VF_loop
    import numba
    import numpy as np
    @numba.jit
    def VFI_loop(V, e, betafirm, sizez, sizek, Vmat, pi):
        V_prime = np.dot(pi, V)
        for i in range(sizez):  # loop over z
            for j in range(sizek):  # loop over k
                for k in range(sizek): # loop over k'
                    Vmat[i, j, k] = e[i, j, k] + betafirm * V_prime[i, k]
        return Vmat
    
    Vmat = VFI_loop(V, e, betafirm, sizez, sizek, Vmat, pi)
    return Vmat
    