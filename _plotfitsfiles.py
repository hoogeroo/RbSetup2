#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 18:41:40 2022

@author: lab
"""

from astropy.io import fits

import numpy as np

import matplotlib.pyplot as plt

import math

import os

def lowpassfilter(data):
    data = np.array(data)
    pic = np.zeros([data.shape[0]-2, data.shape[1]-2])

    for i in [-1, 0, 1]:
        endi = -1+i if -1+i else None

        for j in [-1, 0, 1]:
            endj = -1+j if -1+j else None
            pic += 0.1 * (1 + (not i and not j)) * data[1+i:endi, 1+j:endj]

    return pic

folder='/home/lab/mydata/Data/202501161505/'
nums=[i+1 for i in range(10)]

for num in nums:
    with fits.open(f'{folder}Data_{num}.fit') as f:
        plt.figure(figsize=(4,4))
        data = f[0].data
        pic = [lowpassfilter(data[j,:,:]) for j in range(data.shape[0])]
        OD = -np.log((pic[0]-pic[2]+.1)/(pic[1]-pic[2]+.1))
        plt.imshow(OD)
        plt.xticks([])
        plt.yticks([])
        plt.savefig(f'{folder}06231721-Data_{num}.png', filetype = 'png', dpi=200)
#        
        
#with fits.open(f'{folder}Data_1.fit') as f:
#    testvar = f[1].data