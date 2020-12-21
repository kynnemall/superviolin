# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 14:51:42 2020

@author: Labuser
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

class onionplot:
    
    def __init__(self, x = 'dose', y = 'order', rep_col = 'replicate', subgroup = False,
                 csv_path = 'practice_data.csv', plot_kde = False, print_ = False):
        self.df = pd.read_csv(csv_path)
        self.x = x
        self.y = y
        self.rep = rep_col
        self.subgroups = subgroup
        if self.subgroups:
            self.subgroups = self.df[subgroup].unique()
        self.unique_reps = self.df[self.rep].unique()
        self.p_x, self.w_y = [], []
        self.get_kde_data(print_, plot_kde)
        self.colors = ['Green','Red','Blue','Pink','Purple']
        
    def get_kde_data(self, print_ = False, plot = False):
        min_cuts = []
        max_cuts = []
        for i in range(len(self.unique_reps)):
            sub = self.df[self.df[self.rep] == self.unique_reps[i]]
            min_cuts.append(sub[self.y].min())
            max_cuts.append(sub[self.y].max())
        min_cuts = sorted(min_cuts)
        max_cuts = sorted(max_cuts)
        # make linespace of points from highest_min_cut to lowest_max_cut
        points = list(np.linspace(max(min_cuts), min(max_cuts), num = 128))
        points = sorted(list(set(min_cuts + points + max_cuts)))   
        for a in self.unique_reps:
            sub = self.df[self.df[self.rep] == a][self.y]
            kde = gaussian_kde(sub)
            kde_points = kde.evaluate(points)
            # zero the kde points
            kde_points = kde_points - kde_points.min()
            zeros_present = list(kde_points)
            print(f"{zeros_present.count(0)} zeroes present already at index {zeros_present.index(0)}")
            # use min and max to make the kde_points outside that dataset = 0
            idx_min = min_cuts.index(sub.min())
            idx_max = max_cuts.index(sub.max())
            if idx_min > 0:
                for p in range(idx_min):
                    kde_points[p] = 0
#            print(sub.min())
#            print(points[:3])
#            print(kde_points[:3])
#            print('\n')
            for idx in range(idx_max - len(max_cuts), 0):
                if idx_max - len(max_cuts) != -1:
                    kde_points[idx+1] = 0
#            print(sub.max())
#            print(points[-3:])
#            print(kde_points[-3:])
            self.w_y.append(kde_points)
            self.p_x.append(points)
#        self.check_cutting()
        self.p_x = np.array(self.p_x)
        self.w_y = np.array(self.w_y)
        self.cum_wy = np.cumsum(self.w_y, axis = 0)
        self.norm_wy = self.cum_wy / self.cum_wy.max() # [0,1]
        # plot the data
        if plot:
            plt.figure()
            for i in range(self.w_y.shape[0]):
                plt.plot(self.p_x[i], self.w_y[i])
                
    def check_cutting(self):
        count = 0
        gt = 0
        for i in range(len(self.unique_reps)):
            zero_count = list(self.w_y[i]).count(0)
            count += zero_count
            gt += i * 2
        if gt == count:
            print('Cutting worked')
        else:
            print(f"Cutting failed. {count} zeros found when there should have been {gt}")
            for i in range(3):
                print(onion.w_y[i][:3])
                print(onion.w_y[i][-3:])
                
    def plot_onion(self, total_width = 0.8, linewidth = 2):
        plt.figure()
        violin_y = []
        violin_x = []
        # mirror x and y values to create a continuous line
        for i in range(1, self.w_y.shape[0] + 1):
            reshaped_x = np.append(self.p_x[i-1], np.flipud(self.p_x[i-1]))
            reshaped_y = np.append(self.norm_wy[i-1], np.flipud(self.norm_wy[i-1]) * -1) * total_width
            violin_x.append(reshaped_x)
            violin_y.append(reshaped_y)
        for i in range(1, self.w_y.shape[0] + 1):
            i = i * -1
            plt.fill(violin_y[i], violin_x[i], color = self.colors[i])
    
    def plot_stripes(self, total_width = 0.8, linewidth = 2):
        """
        Don't need to evaluate a new KDE, just use the one from the last subarray of w_y
        DONE: add these distances to p_x to get new x values
        DONE: calculate new y values based on these distances
        DONE: use the last array to plot the outline
        """
        self.right_sides = np.array([self.norm_wy[-1]*-1 + i*2 for i in self.norm_wy])
        # create array of 3 lines which denote the 3 replicates on the plot
        new_wy = []
        for i,a in enumerate(self.p_x):
            if i == 0:
                newline = np.append(self.norm_wy[-1]*-1, np.flipud(self.right_sides[i]))
            else:
                newline = np.append(self.right_sides[i-1], np.flipud(self.right_sides[i]))
            new_wy.append(newline)
        self.new_wy = np.array(new_wy)
        # use last array to plot the outline
        outline_y = np.append(self.p_x[-1], np.flipud(self.p_x[-1]))
        outline_x = np.append(self.norm_wy[-1], np.flipud(self.norm_wy[-1]) * -1) * total_width
        for i in range(self.w_y.shape[0]):
            reshaped_x = np.append(self.p_x[i-1], np.flipud(self.p_x[i-1]))
            plt.fill(self.new_wy[i] * total_width, reshaped_x, color = self.colors[i])
        plt.plot(outline_x, outline_y, color = 'Black', linewidth = linewidth)

onion = onionplot(subgroup = 'dose')
onion.plot_stripes()
plt.ylabel('Fibre alignment')
