# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 14:51:42 2020

@author: Labuser
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

class onionplot:
    
    def __init__(self):
        self.df = pd.read_csv('practice_data.csv')
        self.x = 'dose'
        self.y = 'order'
        self.rep = 'replicate'
        self.p_x, self.w_y = [], []
        
    def plot_distributions(self, close = True):
        for i in range(3):
            plt.subplot(1, 3, i + 1)
            r = self.df[self.rep].unique()
            sub = self.df[self.df[self.rep] == r[i]]
            x, y = sns.kdeplot(sub[self.y], cut = 0).get_lines()[0].get_data()
            self.p_x.append(x)
            self.w_y.append(y)
        if close:
            plt.close()
        self.p_x = np.array(self.p_x)
        self.w_y = np.array(self.w_y)
    
    def stack_kde_data(self):
        # subtract min from y data to get close to a zero line
        self.w_y = self.w_y - np.min(self.w_y, axis=(1), keepdims=True)
        # create y values which stack
        
        # normalize max to a certain range
    
    def plot(self):
        pass
    
# 190703_paBBT_fg or 190711_paBBT_fg
onion = onionplot()
onion.plot_distributions()
onion.stack_kde_data()
#df = onion.df