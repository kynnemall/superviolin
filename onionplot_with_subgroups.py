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
            self.subgroups = sorted(self.df[subgroup].unique().tolist())
        self.unique_reps = self.df[self.rep].unique()
        # make sure there's enough colours for each subgroup when instantiating
        self.colors = ['Green','Red','Blue','Pink','Purple']
        # dictionary of arrays for subgroup data
        # loop through the keys and add an empty list when the replicate numbers don't match
        # this dataset has 22 KDEs to calculate rather than 24
        self.subgroup_dict = dict(zip(self.subgroups,
                                      [{'norm_wy' : [], 'px' : []} for i in self.subgroups])
                                  )
        self.get_kde_data(print_, plot_kde)
        self.palette = None
        
    def get_kde_data(self, print_ = False, plot = False):
        for group in self.subgroups:
            px = []
            norm_wy = []
            min_cuts = []
            max_cuts = []
            for rep in self.unique_reps:
                sub = self.df[(self.df[self.rep] == rep) & (self.df[self.subgroup] == group)]
                min_cuts.append(sub[self.y].min())
                max_cuts.append(sub[self.y].max())
            min_cuts = sorted(min_cuts)
            max_cuts = sorted(max_cuts)
            if print_:
                print(np.nanmax(min_cuts))
                print(np.nanmin(max_cuts))
            # make linespace of points from highest_min_cut to lowest_max_cut
            global points1
            points1 = list(np.linspace(np.nanmax(min_cuts), np.nanmin(max_cuts), num = 128))
            points = sorted(list(set(min_cuts + points1 + max_cuts))) 
            for rep in self.unique_reps:
                # first point when we catch an empty list caused by uneven rep numbers
                try:
                    if print_:
                        print(sub)
                    sub = self.df[(self.df[self.rep] == rep) & (self.df[self.subgroup] == group)]
                    # line below fails for 0.4, figure out why
                    kde = gaussian_kde(sub[self.y])
                    # these kde_points are actual numbers
                    kde_points = kde.evaluate(points)
                    if print_:
                        print(kde_points)
                    # zero the kde points (all are nan for 0.4uM)
                    kde_points = kde_points - np.nanmin(kde_points)
                    # if print_:
                    #     print(kde_points)
                    # zeros_present = list(kde_points)
                    if print_:
                        print('No error')
                        # print(f"{zeros_present.count(0)} zeroes present already at index {zeros_present.index(0)}")
                    # use min and max to make the kde_points outside that dataset = 0
                    # errors with 0.4uM are caused by the following lines
                    idx_min = min_cuts.index(sub[self.y].min())
                    idx_max = max_cuts.index(sub[self.y].max())
                    if idx_min > 0:
                        for p in range(idx_min):
                            kde_points[p] = 0
                    for idx in range(idx_max - len(max_cuts), 0):
                        if idx_max - len(max_cuts) != -1:
                            kde_points[idx+1] = 0
                    norm_wy.append(kde_points)
                    px.append(points)
                    if print_:
                        print('Complete')
                except ValueError:
                    norm_wy.append([])
                    px.append(points)
                    if print_:
                        print('Appending ValueError')
            px = np.array(px)
            # catch the error when there is an empty list added to the dictionary
            length = max([len(e) for e in norm_wy])
            norm_wy = np.array([a if len(a) > 0 else np.zeros(length) for a in norm_wy])
            norm_wy = np.cumsum(norm_wy, axis = 0)
            try:
                norm_wy = norm_wy / norm_wy.max() # [0,1]
            except ValueError:
                print(norm_wy)
            self.subgroup_dict[group]['norm_wy'] = norm_wy
            self.subgroup_dict[group]['px'] = px
    
    def _single_subgroup_plot(self, group, axis_point = 0, total_width = 0.8, linewidth = 2):
        norm_wy = self.subgroup_dict[group]['norm_wy']
        px = self.subgroup_dict[group]['px']
        right_sides = np.array([norm_wy[-1]*-1 + i*2 for i in norm_wy])
        # create array of 3 lines which denote the 3 replicates on the plot
        new_wy = []
        for i,a in enumerate(px):
            if i == 0:
                newline = np.append(norm_wy[-1]*-1, np.flipud(right_sides[i]))
            else:
                newline = np.append(right_sides[i-1], np.flipud(right_sides[i]))
            new_wy.append(newline)
        new_wy = np.array(new_wy)
        # use last array to plot the outline
        outline_y = np.append(px[-1], np.flipud(px[-1]))
        outline_x = np.append(norm_wy[-1], np.flipud(norm_wy[-1]) * -1) * total_width + axis_point
        for i in range(norm_wy.shape[0]):
            reshaped_x = np.append(px[i-1], np.flipud(px[i-1]))
            plt.fill(new_wy[i] * total_width  + axis_point, reshaped_x, color = self.colors[i])
        plt.plot(outline_x, outline_y, color = 'Black', linewidth = linewidth)
        
    def plot_subgroups(self, order = None, centre_val = "mean", middle_vals = "mean",
                       error_bars = ""):
        """
        
        Parameters
        ----------
        order : LIST, optional
            DESCRIPTION. The default is None.
        centre_val : STRING, optional
            DESCRIPTION. Determines where the centre line of the replicates is.
                The default is "mean". "median" is also an option.
        middle_vals : STRING, optional
            DESCRIPTION. Determines whether to use mean or median to measure
                the centrality of each replicate.
                The default is "mean". "median" is also an option.
        error_bars : STRING, optional
            DESCRIPTION. The default is "".

        Returns
        -------
        None.

        """
        ticks = []
        lbls = []
        # width of the bars
        median_width = 0.4
        for i,a in enumerate(self.subgroup_dict.keys()):
            self._single_subgroup_plot(a, i*2)
            ticks.append(i*2)
            lbls.append(a)            
            # calculate the mean/median value for all replicates of the variable
            sub = self.df[self.df[self.x] == a]
            if middle_vals == "mean":
                plt_df = sub.groupby(self.x, as_index = False).agg({self.y : 'mean'})
            else:
                plt_df = sub.groupby(self.x, as_index = False).agg({self.y : 'median'})
            if centre_val == 'mean':
                mid_val = plt_df[self.y].mean()
            else:
                mid_val = plt_df[self.y].median()
            # plot horizontal lines across the column, centered on the tick
            plt.plot([i*2 - median_width / 2, i*2 + median_width / 2],
                     [mid_val, mid_val], lw = 2, color = 'k')
            # plot vertical lines connecting the limits
            
        plt.xticks(ticks, lbls)
        

onion = onionplot(subgroup = 'dose')
# onion.subgroups = [16]
# print('Debugging')
# onion.get_kde_data(print_ = True)
# onion._single_subgroup_plot(0, 1)
onion.plot_subgroups(order = None)
# plt.ylabel('Fibre alignment')
