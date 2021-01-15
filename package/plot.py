# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 14:51:42 2020

@author: Martin Kenny
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

class superplot:    
    def __init__(self, x='drug', y='variable', replicate_column='replicate',
                 filename='demo_data.csv', order="None", centre_val="mean",
                 middle_vals="mean", error_bars="sd", total_width=0.8,
                 linewidth=2, colours='cyan, lightgrey, magenta', dataframe=False):
        errors = []
        # catch errors
        self.df = dataframe
        if 'bool' in str(type(dataframe)):
            if filename.endswith('csv'):
                self.df = pd.read_csv(filename)
            elif ".xl" in filename:
                self.df = pd.read_excel(filename)
            else:
                errors.append("Incorrect filename or unsupported filetype")
        self.x = x
        self.y = y
        self.rep = replicate_column
        missing_cols = []
        for col in [x, y, replicate_column]:
            if col not in self.df.columns:
                missing_cols.append(col)
        if len(missing_cols) != 0:
            if len(missing_cols) == 1:
                errors.append("Variable not found: " + missing_cols[0])
            else:
                errors.append("Missing variables: " + ', '.join(missing_cols))
        if x in self.df.columns:
            self.subgroups = tuple(sorted(self.df[self.x].unique().tolist()))
            if order != "None":
                self.subgroups = "placeholder until order option is implemented"
            else:
                print("This option is not yet implemented")
            # dictionary of arrays for subgroup data
            # loop through the keys and add an empty list when the replicate numbers don't match
            self.subgroup_dict = dict(
                zip(self.subgroups, [{'norm_wy' : [], 'px' : []} for i in self.subgroups])
                )
        if replicate_column in self.df.columns:
            self.unique_reps = tuple(self.df[self.rep].unique())
        # make sure there's enough colours for each subgroup when instantiating
        self.colours = tuple(colours.split(', '))
        # if no errors exist
        if len(errors) == 0:
            self._get_kde_data()
            self._plot_subgroups(centre_val, middle_vals, error_bars,
                                 total_width, linewidth)
        else:
            if len(errors) == 1:
                print("Caught 1 error")
            else:
                print(f"Caught {len(errors)} errors")
            for i,e in enumerate(errors):
                print(f"\t{i+1}. {e}")

    def _get_kde_data(self):
        for group in self.subgroups:
            px = []
            norm_wy = []
            min_cuts = []
            max_cuts = []
            for rep in self.unique_reps:
                sub = self.df[(self.df[self.rep] == rep) & (self.df[self.x] == group)]
                min_cuts.append(sub[self.y].min())
                max_cuts.append(sub[self.y].max())
            min_cuts = sorted(min_cuts)
            max_cuts = sorted(max_cuts)
            # make linespace of points from highest_min_cut to lowest_max_cut
            points1 = list(np.linspace(np.nanmax(min_cuts), np.nanmin(max_cuts), num = 128))
            points = sorted(list(set(min_cuts + points1 + max_cuts))) 
            for rep in self.unique_reps:
                # first point when we catch an empty list caused by uneven rep numbers
                try:
                    sub = self.df[(self.df[self.rep] == rep) & (self.df[self.x] == group)]
                    kde = gaussian_kde(sub[self.y])
                    # these kde_points are actual numbers
                    kde_points = kde.evaluate(points)
                    kde_points = kde_points - np.nanmin(kde_points)
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
                except ValueError:
                    norm_wy.append([])
                    px.append(points)
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
    
    def _single_subgroup_plot(self, group, axis_point, mid_df, middle_vals="mean",
                              total_width=0.8, linewidth=2):
        norm_wy = self.subgroup_dict[group]['norm_wy']
        px = self.subgroup_dict[group]['px']
        right_sides = np.array([norm_wy[-1]*-1 + i*2 for i in norm_wy])
        # create array of 3 lines which denote the 3 replicates on the plot
        new_wy = []
        for i in range(len(px)):
            if i == 0:
                newline = np.append(norm_wy[-1]*-1, np.flipud(right_sides[i]))
            else:
                newline = np.append(right_sides[i-1], np.flipud(right_sides[i]))
            new_wy.append(newline)
        new_wy = np.array(new_wy)
        # use last array to plot the outline
        outline_y = np.append(px[-1], np.flipud(px[-1]))
        outline_x = np.append(norm_wy[-1], np.flipud(norm_wy[-1]) * -1) * total_width + axis_point
        for i,a in enumerate(self.unique_reps):
            reshaped_x = np.append(px[i-1], np.flipud(px[i-1]))
            mid_val = mid_df[mid_df[self.rep] == a][self.y].values
            reshaped_y = new_wy[i] * total_width  + axis_point
            plt.fill(reshaped_y, reshaped_x, color=self.colours[i])
            # get the mid_val each replicate and find it in reshaped_x
            # then get corresponding point in reshaped_x to plot the points
            if mid_val.size > 0: # account for empty mid_val
                arr = reshaped_x[np.logical_not(np.isnan(reshaped_x))]
                nearest = self.find_nearest(arr, mid_val[0])
                # find the index of nearest in new_wy
                idx = np.where(reshaped_x == nearest)
                x_vals = reshaped_y[idx]
                x_val = x_vals[0] + ((x_vals[1] - x_vals[0]) / 2)
                plt.scatter(x_val, mid_val[0], facecolors='none', edgecolors='Black', marker='o')
        plt.plot(outline_x, outline_y, color='Black', linewidth=linewidth)
        
    def _plot_subgroups(self, centre_val, middle_vals,
                       error_bars, total_width, linewidth):
        if len(self.subgroups) > 3:
            plt.figure(figsize=(6, 3))
        else:
            plt.figure(figsize=(3, 3))
        ticks = []
        lbls = []
        # width of the bars
        median_width = 0.4
        for i,a in enumerate(self.subgroups):
            ticks.append(i*2)
            lbls.append(a)            
            # calculate the mean/median value for all replicates of the variable
            sub = self.df[self.df[self.x] == a]
            means = sub.groupby(self.rep, as_index=False).agg({self.y : centre_val})
            plt_df = sub.groupby(self.x, as_index=False).agg({self.y : middle_vals})
            self._single_subgroup_plot(a, i*2, mid_df=means, middle_vals=middle_vals, 
                                       total_width=total_width)
            # get mean or median line of the skeleton plot
            if centre_val == 'mean':
                mid_val = plt_df[self.y].mean()
            else:
                mid_val = plt_df[self.y].median()
            # get error bars for the skeleton plot
            if error_bars == "sd":
                upper = mid_val + means[self.y].std()
                lower = mid_val - means[self.y].std()
            elif error_bars == "ci":
                print("TODO: implement this")
            # plot horizontal lines across the column, centered on the tick
            for b in [mid_val, upper, lower]:
                plt.plot([i*2 - median_width / 2, i*2 + median_width / 2],
                         [b, b], lw=linewidth, color='k')
            # plot vertical lines connecting the limits
            plt.plot([i*2, i*2], [lower, upper], lw=2, color='k')  
        plt.xticks(ticks, lbls)
        
    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

testing = True
if testing:
    import os
    os.chdir('templates')
    test = superplot()
#    plt.close()
    # test.subgroups = [16]
    # print('Debugging')
    # test.get_kde_data(print_ = True)
    # test._single_subgroup_plot(0, 1)

