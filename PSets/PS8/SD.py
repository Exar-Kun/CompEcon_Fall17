#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 08:28:57 2017

@author: Alexandria
"""
def main(PF, pi, Gamma, sizez, sizek):

    import numba
    import numpy as np
    @numba.jit
    def SD_loop(PF, pi, Gamma, sizez, sizek):
        HGamma = np.zeros((sizez, sizek))
        for i in range(sizez):  # z
            for j in range(sizek):  # k
                for m in range(sizez):  # z'
                    HGamma[m, PF[i, j]] = \
                        HGamma[m, PF[i, j]] + pi[i, m] * Gamma[i, j]
        return HGamma
    
    HGamma = SD_loop(PF, pi, Gamma, sizez, sizek)
    return HGamma