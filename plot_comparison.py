# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 14:51:42 2020

@author: Martin Kenny
"""

import os
import seaborn as sns
import numpy as np
import pandas as pd
import scikit_posthocs as sp
import matplotlib.pyplot as plt
from matplotlib import rcParams as params
from scipy.stats import gaussian_kde, norm, kruskal, f_oneway
from scipy.stats import shapiro, mannwhitneyu, ttest_ind
params['xtick.labelsize'] = 8
params['ytick.labelsize'] = 8
params['axes.labelsize'] = 9
params['axes.spines.right'] = False
params['axes.spines.top'] = False
params['figure.dpi'] = 300
params['savefig.dpi'] = 300

class superplot:    
    def __init__(self, x='drug', y='variable', replicate_column='replicate',
                 filename='demo_data.csv', order="None", centre_val="mean",
                 middle_vals="mean", error_bars="SD", total_width=0.8,
                 linewidth=1, cmap='Set2', dataframe=False):
        errors = []
        # check filetype
        # will fail if filename spelled incorrectly
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
                self.subgroups = order.split(', ')
            # dictionary of arrays for subgroup data
            # loop through the keys and add an empty list when the replicate numbers don't match
            self.subgroup_dict = dict(
                zip(self.subgroups, [{'norm_wy' : [], 'px' : []} for i in self.subgroups])
                )
        if replicate_column in self.df.columns:
            self.unique_reps = tuple(self.df[self.rep].unique())
            if len(self.unique_reps) == 6:
                self.unique_reps = ['180807_paBBT_fg_adhesion_nodules.csv',
                                    '190703_paBBT_fg_adhesion_nodules.csv',
                                    '190711_paBBT_fg_adhesion_nodules.csv',
                                    '180725_copy',
                                    '20200429_P-selectin_paBBT_adhesion_nodules.csv',
                                    '180725_paBBT_fg_adhesion_nodules.csv']
            # make sure there's enough colours for each subgroup when instantiating
            if ',' in cmap:
                self.colours = tuple(cmap.split(', '))
            else:
                self.cm = plt.get_cmap(cmap)
#                self.colours = [self.cm(i / len(self.unique_reps)) for i in range(len(self.unique_reps))]
                self.colours = [self.cm(i / 8) for i in range(len(self.unique_reps))]
            if len(self.colours) < len(self.unique_reps):
                print(len(self.colours))
                print(len(self.unique_reps))
                errors.append("Not enough colours for each replicate")
            
        # if no errors exist, create the superplot. Otherwise, report errors
        if len(errors) == 0:
            self.get_kde_data()
            self._plot_subgroups(centre_val, middle_vals, error_bars,
                                 total_width, linewidth)
            self.statistics()
        else:
            if len(errors) == 1:
                print("Caught 1 error")
            else:
                print(f"Caught {len(errors)} errors")
            for i,e in enumerate(errors):
                print(f"\t{i+1}. {e}")

    def get_kde_data(self):
        for group in self.subgroups:
            px = []
            norm_wy = []
            min_cuts = []
            max_cuts = []
            
            # get limits for fitting the kde 
            for rep in self.unique_reps:
                sub = self.df[(self.df[self.rep] == rep) & (self.df[self.x] == group)][self.y]
                min_cuts.append(sub.min())
                max_cuts.append(sub.max())
            min_cuts = sorted(min_cuts)
            max_cuts = sorted(max_cuts)
            # make linespace of points from highest_min_cut to lowest_max_cut
            points1 = list(np.linspace(np.nanmin(min_cuts), np.nanmax(max_cuts), num = 128))
            points = sorted(list(set(min_cuts + points1 + max_cuts))) 
            for rep in self.unique_reps:
                # first point to catch an empty list caused by uneven rep numbers
                try:
                    sub = self.df[(self.df[self.rep] == rep) & (self.df[self.x] == group)][self.y]
                    arr = np.array(sub)
                    # remove nan or inf values which could cause a kde ValueError
                    arr = arr[~(np.isnan(arr))]
                    kde = gaussian_kde(arr)
                    kde_points = kde.evaluate(points)
                    kde_points = kde_points - np.nanmin(kde_points)
                    # use min and max to make the kde_points outside that dataset = 0
                    idx_min = min_cuts.index(arr.min())
                    idx_max = max_cuts.index(arr.max())
                    if idx_min > 0:
                        for p in range(idx_min):
                            kde_points[p] = 0
                    for idx in range(idx_max - len(max_cuts), 0):
                        if idx_max - len(max_cuts) != -1:
                            kde_points[idx+1] = 0
                    # remove nan from arrays prior to combining into dictionary
                    kde_wo_nan = self._interpolate_nan(kde_points)
                    points_wo_nan = self._interpolate_nan(points)
                    norm_wy.append(kde_wo_nan)
                    px.append(points_wo_nan)
                except ValueError:
                    norm_wy.append([])
                    px.append(self._interpolate_nan(points))
            px = np.array(px)
            # catch the error when there is an empty list added to the dictionary
            length = max([len(e) for e in norm_wy])
            # rescale norm_wy for display purposes
            norm_wy = np.array([a if len(a) > 0 else np.zeros(length) for a in norm_wy])
            norm_wy = np.cumsum(norm_wy, axis = 0)
            try:
                norm_wy = norm_wy / np.max(norm_wy) # [0,1]
            except ValueError:
                print('Failed to normalize y values')
            # update the dictionary with the normalized data and corresponding x points
            self.subgroup_dict[group]['norm_wy'] = norm_wy
            self.subgroup_dict[group]['px'] = px
            
    def _interpolate_nan(self, arr):
        diffs = np.diff(arr, axis=0)
        median_val = np.nanmedian(diffs)
        nan_idx = np.where(np.isnan(arr))
        if nan_idx[0].size != 0:
            arr[nan_idx[0][0]] = arr[nan_idx[0][0] + 1] - median_val
        return arr
    
    def _single_subgroup_plot(self, group, axis_point, mid_df,
                              total_width=0.8, linewidth=1):
        # select scatter size based on number of replicates
        scatter_sizes = [12, 10, 8, 6]
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
            plt.plot(reshaped_y, reshaped_x, c='k', linewidth=0.5)
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
        
    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]
    
    def statistics(self, centre_val='mean', x2=2):
        """
        1. Get central values for statistics
        2. Check normality
        3. Check for more than 2 groups
        4. Generate statistics
        5. Plot the statistics if only 2 or 3 groups to compare
        """
        means = self.df.groupby([self.rep, self.x], as_index=False).agg({self.y : centre_val})
        normal = self._normality(means)
        data = [list(means[means[self.x] == i][self.y]) for i in means[self.x].unique()]
        if len(self.subgroups) > 2:
            # compare more than 2 groups
            if normal:
                stat, p = f_oneway(*data)
                # use tukey to compare all groups with Bonferroni correction
                posthoc = sp.posthoc_tukey(means, self.y, self.x)
                print(f"One-way ANOVA P-value: {p:.3f}")
                print('Tukey posthoc tests conducted')
            else:
                stat, p = kruskal(*data)
                posthoc = sp.posthoc_mannwhitney(means, self.y, self.x, p_adjust='bonferroni')
                print(f"Kruskal-Wallis P-value: {p:.3f}")
                print('Mann-Whitney posthoc tests conducted with Bonferroni correction')
            # save statistics to file
            posthoc.to_csv(f'posthoc_statistics_{self.y}.txt', sep='\t')
            print("Posthoc statistics saved to txt file")
        else:
            # compare only 2 groups
            if normal:
                stat, p = ttest_ind(data[0], data[1])
                if p < 0.0001:
                    print(f"Independent t-test P-value: {p:.2e}")
                else:
                    print(f"Independent t-test P-value: {p:.3f}")
            else:
                stat, p = mannwhitneyu(data[0], data[1])
                if p < 0.0001:
                    print(f"Mann-Whitney P-value: {p:.2e}")
                else:
                    print(f"Mann-Whitney P-value: {p:.3f}")
                    
        # plot statistics if only 2 or 3 groups
        ax = plt.gca()
        low, high = ax.get_ylim()
        span = high - low
        increment = span * 0.03 # add high to get the new y value
        if len(self.subgroups) == 2:
            x1 = 0
            y = increment + high
            h = y + increment
            plt.plot([x1, x1, x2, x2], [y, h, h, y], lw=1, c='k')
            plt.text((x1+x2)*.5, h, f"P = {p:.3f}", ha='center', va='bottom',
                     color='k', fontsize=8)
            plt.ylim((low, high+increment*10))
        elif len(self.subgroups) == 3:
            labels = [i._text for i in ax.get_xticklabels()]
            pairs = ((0, 1), (1, 2), (0, 2))
            y = increment + high # increment = 3% of the range of the y-axis
            text_loc = ['center', 'center', 'center']
            for i,pair in enumerate(pairs):
                # get posthoc statistic for each comparison
                condition1, condition2 = [labels[i] for i in pair]
                pval = posthoc.loc[condition1, condition2]
                x1, x2 = [i * 2 for i in pair]
                # calculate values for lines and locating p-values on plot
                h = y * 1.02
                y += increment * 5
                # plot the posthoc p-values and lines
                plt.plot([x1, x1, x2, x2], [h, y, y, h], lw=1, c='Black')
                plt.text((x1+x2)/2, y, f"P = {pval:.3f}", ha=text_loc[i],
                         va='bottom', color='Black', fontsize=8)
            plt.ylim((low, low + span * 1.5))
    
    def _normality(self, data):
        lst = []
        for group in self.subgroups:
            group_var = data[data[self.x] == group][self.y]
            stat, p = shapiro(group_var)
            lst.append(p)
        normal = [1 if i > 0.05 else 0 for i in lst]
        if np.mean(normal) > 0.65:
            return True
        else:
            return False
        
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

# testing code
# make ideal superplot
os.chdir('templates')
test = superplot()
plt.ylabel('Spreading area ($\mu$$m^2$)')
#ax = plt.gca()
#ylims = ax.get_ylim()
##plt.close()
## make Lord et al. SuperPlot
for x in range(6):
    if x != 1:
        test.x_vals[x] /= 2
test.beeswarm_plot(0.8,1)
test.statistics(x2=1)
ax = plt.gca()
ax.legend_ = None
#plt.ylabel('Spreading area ($\mu$$m^2$)')
#plt.ylim(ylims)
## SuperPlot with 6 replicates
os.chdir(r'C:\Users\martinkenny\OneDrive - Royal College of Surgeons in Ireland\Documents\Writing\My papers\Superplot letter')
df = pd.read_csv('20210126_6_replicates.csv')
spread = df[df['variable'] <= 55]
test = superplot(x='drug', y='variable', dataframe=spread, replicate_column='rep')
plt.ylabel('Spreading area ($\mu$$m^2$)')
#plt.ylim(ylims)
