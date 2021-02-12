# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 11:15:28 2021

@author: martinkenny
"""

import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from plot import superplot
#params['xtick.labelsize'] = 8
#params['ytick.labelsize'] = 8
#params['axes.labelsize'] = 9
#params['axes.spines.right'] = False
#params['axes.spines.top'] = False

class super_figure(superplot):
    
    def _single_subgroup_plot(self, group, axis_point, mid_df,
                              total_width=0.8, linewidth=1):
        # select scatter size based on number of replicates
        scatter_sizes = [14, 12, 10, 8]
        if len(self.unique_reps) < 3:
            num = 0 
        elif len(self.unique_reps) > len(scatter_sizes):
            num = -1
        else:
            num = len(self.unique_reps) - 3
        scatter_size = scatter_sizes[num]
        
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
        """
        The problem with gapping in group 2 appears to be caused by reshaping the arrays
        Find the issue in this function. Length of outline_x or outline_wy isn't the issue.
        The issue is within the end values of outline_x which should be integer values,
        but instead they are offset floats. Implemented temporary fix;
        find original source of the bug later
        """
        if outline_x[0] != outline_x[-1]:
            xval = round(outline_x[0])
            yval = outline_y[0]
            outline_x = np.insert(outline_x, 0, xval)
            outline_x = np.insert(outline_x, outline_x.size, xval)
            outline_y = np.insert(outline_y, 0, yval)
            outline_y = np.insert(outline_y, outline_y.size, yval)
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
                # find the indices of nearest in new_wy
                # there will be two because new_wy is a loop
                idx = np.where(reshaped_x == nearest)
                x_vals = reshaped_y[idx]
                x_val = x_vals[0] + ((x_vals[1] - x_vals[0]) / 2)
                plt.scatter(x_val, mid_val[0], facecolors='none', edgecolors='Black',
                            zorder=2, marker='o', s=scatter_size)
                self.x_vals.append(x_val)
                self.mid_vals.append(mid_val[0])
        plt.plot(outline_x, outline_y, color='Black', linewidth=linewidth)
        
    def _plot_subgroups(self, centre_val, middle_vals,
                       error_bars, total_width, linewidth):
        self.x_vals = []
        self.mid_vals = []
        width = 1 + len(self.subgroups) / 2
        height = 5 / 2.54
        plt.figure(figsize=(width, height))
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
            self._single_subgroup_plot(a, i*2, mid_df=means, total_width=total_width)
            # get mean or median line of the skeleton plot
            if centre_val == 'mean':
                mid_val = plt_df[self.y].mean()
            else:
                mid_val = plt_df[self.y].median()
            # get error bars for the skeleton plot
            if error_bars == "SD":
                upper = mid_val + means[self.y].std()
                lower = mid_val - means[self.y].std()
            else:
                lower,upper = norm.interval(0.95, loc=means[self.y].mean(),
                                      scale=means[self.y].std())
            # plot horizontal lines across the column, centered on the tick
            plt.plot([i*2 - median_width / 1.5, i*2 + median_width / 1.5],
                         [mid_val, mid_val], lw=linewidth, color='k')
            for b in [upper, lower]:
                plt.plot([i*2 - median_width / 4.5, i*2 + median_width / 4.5],
                         [b, b], lw=linewidth, color='k')
            # plot vertical lines connecting the limits
            plt.plot([i*2, i*2], [lower, upper], lw=linewidth, color='k')  
        plt.xticks(ticks, lbls)
    
    def beeswarm_plot(self, total_width, linewidth):
        width = 1 + len(self.subgroups) / 2
        height = 5 / 2.54
        plt.figure(figsize=(width, height))
        sns.swarmplot(x = self.x, y = self.y, data = self.df, hue = self.rep, size = 2,
                      palette = self.colours)
        ticks = []
        lbls = []
        # width of the bars
        median_width = 0.4
        for i,a in enumerate(self.subgroups):
            ticks.append(i)
            lbls.append(a)            
            # calculate the mean/median value for all replicates of the variable
            sub = self.df[self.df[self.x] == a]
            means = sub.groupby(self.rep, as_index=False).agg({self.y : 'mean'})
            plt_df = sub.groupby(self.x, as_index=False).agg({self.y : 'mean'})
            # get mean or median line of the skeleton plot
            mid_val = plt_df[self.y].mean()
            upper = mid_val + means[self.y].std()
            lower = mid_val - means[self.y].std()
            # plot horizontal lines across the column, centered on the tick
            plt.plot([i - median_width / 3, i + median_width / 3],
                         [mid_val, mid_val], lw=linewidth, color='k', zorder=10)
            for b in [upper, lower]:
                plt.plot([i - median_width / 8, i + median_width / 8],
                         [b, b], lw=linewidth, color='k',zorder=10)
            # plot vertical lines connecting the limits
            plt.plot([i, i], [lower, upper], lw=1, color='k',zorder=10) 
        plt.xticks(ticks, lbls)
        plt.xlabel('')
        for a,b,c in zip(self.x_vals, self.mid_vals, self.colours+self.colours):
            plt.scatter(a, b, facecolors=c, edgecolors='Black',
                        zorder=10, marker='o', s=15)
    
    
os.chdir('templates')
test = superplot()
plt.ylabel('Spreading area ($\mu$$m^2$)')
#plt.close()
# make Lord et al. SuperPlot
for x in range(6):
    if x != 1:
        test.x_vals[x] /= 2
test.beeswarm_plot(0.8,1)
test.statistics(x2=1)
ax = plt.gca()
ax.legend_ = None
plt.ylabel('Spreading area ($\mu$$m^2$)')
# SuperPlot with 6 replicates
os.chdir(r'C:\Users\martinkenny\OneDrive - Royal College of Surgeons in Ireland\Documents\Writing\My papers\Superplot letter')
test = superplot(x='drug', y='variable', filename='20210126_6_replicates.csv', replicate_column='rep')
plt.ylabel('Spreading area ($\mu$$m^2$)')