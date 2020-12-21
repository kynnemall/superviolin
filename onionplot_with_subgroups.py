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
        self.subgroup = subgroup
        if self.subgroup:
            self.subgroups = self.df[subgroup].unique()
        self.unique_reps = self.df[self.rep].unique()
        # make sure there's enough colours for each subgroup when instantiating
        self.colors = ['Green','Red','Blue','Pink','Purple']
        self.get_kde_data(print_, plot_kde)
        # dictionary of arrays for subgroup data
        # loop through the keys and add an empty list when the replicate numbers don't match
        # this dataset has 22 KDEs to calculate rather than 24
        self.subgroup_dict = dict(zip(self.subgroups, [{'norm_wy' : [], 'px' : []}
                                                        for i in self.subgroups]))
        # self.plot_stripes()
        self.palette = None
        
    def get_kde_data(self, print_ = False, plot = False):
        for group in self.subgroups:
            px = []
            norm_wy = []
            min_cuts = []
            max_cuts = []
            for rep in self.unique_reps:
                print(group, rep)
                sub = self.df[(self.df[self.rep] == rep) & (self.df[self.subgroup] == group)]
                min_cuts.append(sub[self.y].min())
                max_cuts.append(sub[self.y].max())
            min_cuts = sorted(min_cuts)
            max_cuts = sorted(max_cuts)
            # make linespace of points from highest_min_cut to lowest_max_cut
            points = list(np.linspace(max(min_cuts), min(max_cuts), num = 128))
            points = sorted(list(set(min_cuts + points + max_cuts))) 
            for rep in self.unique_reps:
                # first point when we catch an empty list caused by uneven rep numbers
                try:
                    kde = gaussian_kde(sub[self.y])
                    kde_points = kde.evaluate(points)
                    # zero the kde points
                    kde_points = kde_points - kde_points.min()
                    zeros_present = list(kde_points)
                    if print_:
                        print(f"{zeros_present.count(0)} zeroes present already at index {zeros_present.index(0)}")
                    # use min and max to make the kde_points outside that dataset = 0
                    idx_min = min_cuts.index(sub.min())
                    idx_max = max_cuts.index(sub.max())
                    if idx_min > 0:
                        for p in range(idx_min):
                            kde_points[p] = 0
                    for idx in range(idx_max - len(max_cuts), 0):
                        if idx_max - len(max_cuts) != -1:
                            kde_points[idx+1] = 0
                    norm_wy.append(kde_points)
                    px.append(points)
                except ValueError:
                    norm_wy.append([])
                    px.append([])
            print(f'completed group {group}')
            px = np.array(px)
            print(px.shape)
            # catch the error when there is an empty list added to the dictionary
            try:
                norm_wy = np.array(norm_wy)
            except:
                length = max([len(e) for e in norm_wy])
                norm_wy = [a if len(a) > 0 else np.zeros(length) for a in enumerate(norm_wy) ]
            norm_wy = np.cumsum(norm_wy, axis = 0)
            try:
                norm_wy = norm_wy / norm_wy.max() # [0,1]
            except ValueError:
                print(norm_wy)
            self.subgroup_dict[group]['norm_wy'] = norm_wy
            self.subgroup_dict[group]['px'] = px
            # work out how to append and then insert into the dictionary
                
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
        Only norm_wy and p_x used for this function
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
        for i in range(self.norm_wy.shape[0]):
            reshaped_x = np.append(self.p_x[i-1], np.flipud(self.p_x[i-1]))
            plt.fill(self.new_wy[i] * total_width, reshaped_x, color = self.colors[i])
        plt.plot(outline_x, outline_y, color = 'Black', linewidth = linewidth)

onion = onionplot(subgroup = 'dose')
#onion.plot_stripes()
#plt.ylabel('Fibre alignment')
