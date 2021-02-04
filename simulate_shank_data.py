# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 14:09:55 2021

@author: philc
"""
#%% Get relevent modules

import numpy as np
import pandas as pd
import itertools
import time
import sys
import matplotlib.pyplot as plt

#%% Get demo data that was collected by me 

demoData = pd.read_table("demo.txt", sep = ",")

# def datasim(row = i, data = demoData, channel = "Node03.lax"):
#     print(data.loc[row,channel])
#     return(data.loc[row, channel])

# for i in range(1,len(demoData)):
#     datasim()


# If I want to create continuous loop...
# contData = itertools.cycle(demoData['Node03.lax'])

#%%

def shiftnadd(list_to_shift, val_to_add):
    newlist = list_to_shift[1:] # drop first sample
    newlist = np.append(newlist, val_to_add) # append new sample to end of window  
    return(newlist)

try:
    plotWindow = 3 #seconds: sampling rate of sensors is 100 Hz
    RShank_lax = np.zeros(plotWindow*100) # initialize empty vectors for plotting at 100 Hz
    RShank_lay = np.zeros(plotWindow*100)
    RShank_laz = np.zeros(plotWindow*100)
    
    fig = plt.figure()
    
    for i in demoData['Node03.lax']:
        
        # plt.clf()
        
        print(i)
        
        # RShank_lax = shiftnadd(RShank_lax, i)

        # plt.plot(range(0,300), RShank_lax)
        # plt.pause(0.000001)   
        
        time.sleep(0.01)

except KeyboardInterrupt:
    sys.exit("User interrupt")
