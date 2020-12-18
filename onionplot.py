# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 14:51:42 2020

@author: Labuser
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

class onionplot:
    
    def __init__(self):
        self.df = pd.read_csv('practice_data.csv')
        self.x = 'dose'
        self.y = 'order'
        self.rep = 'replicate'
        self.unique_reps = self.df[self.rep].unique()
        self.p_x, self.w_y = [], []
        
    def get_kde_data(self, plot = False):
        min_cuts = []
        max_cuts = []
        for i in range(len(self.unique_reps)):
            sub = self.df[self.df[self.rep] == self.unique_reps[i]]
            min_cuts.append(sub[self.y].min())
            max_cuts.append(sub[self.y].max())
        min_cuts = sorted(min_cuts)
        max_cuts = sorted(max_cuts)
        # make linespace of points from highest_min_cut t0 lowest_max_cut
        points = list(np.linspace(max(min_cuts), min(max_cuts), num = 128))
        points = sorted(list(set(min_cuts + points + max_cuts)))   
        for a in self.unique_reps:
            sub = self.df[self.df[self.rep] == a][self.y]
            kde = gaussian_kde(sub)
            kde_points = kde.evaluate(points)
            # zero the kde points
            kde_points = kde_points - kde_points.min()
            # use min and max to make the kde_points outside that dataset = 0
            idx_min = min_cuts.index(sub.min())
            idx_max = max_cuts.index(sub.max())
            if idx_min > 0:
                for p in range(idx_min):
                    kde_points[p] = 0
            for idx in range(idx_max - len(max_cuts), 0):
                kde_points[idx+1] = 0
            self.w_y.append(kde_points)
            self.p_x.append(points)
        self.p_x = np.array(self.p_x)
        self.w_y = np.array(self.w_y)
        # stack the values for plotting
        self.w_y = np.cumsum(self.w_y, axis = 0)
        # normalize the data to range [0,1]
        self.w_y = self.w_y / self.w_y.max()
        # plot the data
        if plot:
            plt.figure()
            for i in range(self.w_y.shape[0]):
                plt.plot(self.p_x[i], self.w_y[i])
                
    def plot_onion(self, total_width = 0.8, linewidth = 2):
        plt.figure()
        violin_y = []
        violin_x = []
        colors = ['Green','Red','Blue','Pink','Purple']
        # mirror x and y values to create a continuous line
        for i in range(self.w_y.shape[0]):
            reshaped_x = np.append(self.p_x[i], np.flipud(self.p_x[i]))
            reshaped_y = np.append(self.w_y[i], np.flipud(self.w_y[i]) * -1) * total_width
            violin_x.append(reshaped_x)
            violin_y.append(reshaped_y)
        for i in range(1, self.w_y.shape[0] + 1):
            i = i * -1
            print(colors[i])
            plt.plot(violin_y[i], violin_x[i], color = colors[i], linewidth = linewidth)
            plt.fill(violin_y[i], violin_x[i], color = colors[i])
            #plt.fill_between(violin_y[i], violin_x[i], color = colors[i])
            
    def simple_alternative(self):
        w = 0.8
        colors = ['LightGreen','LightBlue','Red','Purple','Brown']
        reps = self.df[self.rep].unique().tolist()
        for i,a in enumerate(self.unique_reps[::-1]):
            sub = self.df[self.df[self.rep].isin(reps)]
            sns.violinplot(x = 'dose', y = 'order', data = sub, cut = 0,
                           width = w, inner = None, color = colors[i])
            w -= 0.2

onion = onionplot()
onion.get_kde_data()
onion.plot_onion()
