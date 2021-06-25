# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 14:51:42 2020

@author: Martin Kenny
"""

import os
import numpy as np
import pandas as pd
import scikit_posthocs as sp
import matplotlib.pyplot as plt
from matplotlib import rcParams as params
from scipy.stats import gaussian_kde, norm, f_oneway
from scipy.stats import ttest_ind, ttest_rel
params["xtick.labelsize"] = 8
params["ytick.labelsize"] = 8
params["axes.labelsize"] = 9
params["axes.spines.right"] = False
params["axes.spines.top"] = False
params["figure.dpi"] = 300
params['legend.fontsize'] = 5

class Superviolin:
    def __init__(self, filename, data_format, condition="condition", 
                 value="value", replicate="replicate", order="None",
                 centre_val="mean", middle_vals="mean", error_bars="SEM",
                 paired_data="no", stats_on_plot="no", ylimits="None",
                 total_width=0.8, linewidth=1, dataframe=False, dpi=300,
                 sep_linewidth=0.5, xlabel="", ylabel="", cmap="Set2",
                 bw="None", show_legend="no"):
        self.errors = []
        self.df = dataframe
        self.x = condition if condition != "REPLACE_ME" else "condition"
        self.y = value if value != "REPLACE_ME" else "value"
        self.rep = replicate if replicate != "REPLACE_ME" else "replicate"
        self.linewidth = linewidth
        self.sep_linewidth = sep_linewidth
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.middle_vals = middle_vals
        self.centre_val = centre_val
        self.paired = paired_data
        self.stats_on_plot = stats_on_plot
        self.ylimits = ylimits
        self.total_width = total_width
        self.error_bars = error_bars
        self.show_legend = show_legend
        self._on_legend = []
        if bw != "None":
            self.bw = bw
        else:
            self.bw = None
        params["savefig.dpi"] = dpi
        if self.xlabel == "REPLACE_ME":
            self.xlabel = ""
        if self.ylabel == "REPLACE_ME":
            self.ylabel = ""
            
        qualitative = ["Pastel1", "Pastel2", "Paired", "Accent", "Dark2",
                       "Set1", "Set2", "Set3", "tab10", "tab20", "tab20b",
                       "tab20c"]
        
        # ensure dataframe is loaded
        if self._check_df(filename, data_format):
            
            # ensure columns are all present in the dataframe
            if self._cols_in_df():
                
                # force Condition and Replicate to string types
                self.df[self.x] = self.df[self.x].astype(str)
                self.df[self.rep] = self.df[self.rep].astype(str)
                
                # organize subgroups
                self.subgroups = tuple(sorted(self.df[self.x].unique().tolist()))
                if order != "None":
                    self.subgroups = order.split(", ")
                
                # dictionary of arrays for subgroup data
                # loop through the keys and add an empty list
                # when the replicate numbers don"t match
                self.subgroup_dict = dict(
                    zip(self.subgroups,
                        [{"norm_wy" : [], "px" : []} for i in self.subgroups])
                    )
    
                self.unique_reps = tuple(self.df[self.rep].unique())
                
                # make sure there"s enough colours for 
                # each subgroup when instantiating
                if ", " in cmap:
                    self.colours = tuple(cmap.split(", "))
                else:
                    self.cm = plt.get_cmap(cmap)
                    if cmap in qualitative:
                        # self.colours = [self.cm(i / len(self.unique_reps)) for i in range(len(self.unique_reps))]
                        self.colours = [self.cm(i / self.cm.N) for i in range(len(self.unique_reps))]
                    else:
                        divisor = len(self.unique_reps)+2
                        self.colours = [self.cm((i+2) / divisor) for i in range(len(self.unique_reps))]
                        # shuffle colours
                        np.random.shuffle(self.colours)
                if len(self.colours) < len(self.unique_reps):
                    self.errors.append("Not enough colours for each replicate")
                    
    def generate_plot(self):
        """
        Generate Violin SuperPlot by calling get_kde_data, plot_subgroups,
        and get_statistics if the errors list attribute is empty.

        Returns
        -------
        None.

        """
        # if no errors exist, create the superplot. Otherwise, report errors
        if len(self.errors) == 0:
            self.get_kde_data(self.bw)
            self.plot_subgroups(self.centre_val, self.middle_vals,
                                self.error_bars, self.ylimits,
                                self.total_width, self.linewidth,
                                self.stats_on_plot, self.show_legend)
            self.get_statistics(self.centre_val, self.paired,
                                self.stats_on_plot, self.ylimits)
        else:
            if len(self.errors) == 1:
                print("Caught 1 error")
            else:
                print(f"Caught {len(self.errors)} errors")
            for i,e in enumerate(self.errors, 1):
                print(f"\t{i}. {e}")
                            
    def _make_tidy(self, xl_file):
        """
        Convert excel workbook from sheets containing replicate data to a tidy
        data format for generating Violin SuperPlots

        Parameters
        ----------
        xl_file : string
            name of the excel file being examined

        Returns
        -------
        None.

        """
        xl = pd.ExcelFile(xl_file)
        sheets = xl.sheet_names # replicates
        dfs = []
        for s in sheets:
            df = xl.parse(s)
            if not df.empty:
                df = df.melt(value_vars=df.columns.tolist(), var_name=self.x,
                             value_name=self.y)
                df[self.rep] = s
                dfs.append(df)
        self.df = pd.concat(dfs)
    
    def _check_df(self, filename, data_format):
        """
        

        Parameters
        ----------
        filename : string
            name of the file containing the data for the Violin SuperPlot.
            Must be CSV or an Excel workbook
        data_format : string
            either "tidy" or "untidy" based on format of the data

        Returns
        -------
        bool
            True, if a Pandas DataFrame object was created using the filename,
            else False

        """
        if "bool" in str(type(self.df)):
            if filename.endswith("csv") and filename in os.listdir():
                self.df = pd.read_csv(filename)
                return True
            elif ".xl" in filename and filename in os.listdir():
                if data_format == "tidy":
                    self.df = pd.read_excel(filename)
                else:
                    self._make_tidy(filename)
                return True
            else:
                self.errors.append("Incorrect filename or unsupported filetype")
                return False
        else:
            return True
    
    def _cols_in_df(self):
        """
        Check if all column names specified by the user are present in the 
        self.df DataFrame

        Returns
        -------
        bool
            True if all supplied column names are present in the df attribute

        """
        cols = [self.x, self.y, self.rep]
        missing_cols = [col for col in cols if col not in self.df.columns]
        if len(missing_cols) != 0:
            if len(missing_cols) == 1:
                self.errors.append("Variable not found: " + missing_cols[0])
            else:
                add_on = "Missing variables: " + ", ".join(missing_cols)
                self.errors.append(add_on)
            return False
        else:
            return True

    def get_kde_data(self, bw=None):
        """
        Fit kernel density estimators to each replicate of each condition,
        generate list of x and y co-ordinates of the histogram,
        stack them, and add the data to the subgroup_dict attribute

        Parameters
        ----------
        bw : float
            The percent smoothing to apply to the stripe outlines.
            Values should be between 0 and 1. The default value will result
            in an "optimal" value being used to smoothen the stripes. This
            value is calculated using Scott's Rule

        Returns
        -------
        None.

        """
        for group in self.subgroups:
            px = []
            norm_wy = []
            min_cuts = []
            max_cuts = []
            
            # get limits for fitting the kde 
            for rep in self.unique_reps:
                sub = self.df[(self.df[self.rep] == rep) &
                              (self.df[self.x] == group)][self.y]
                min_cuts.append(sub.min())
                max_cuts.append(sub.max())
            min_cuts = sorted(min_cuts)
            max_cuts = sorted(max_cuts)
            
            # make linespace of points from highest_min_cut to lowest_max_cut
            points1 = list(np.linspace(np.nanmin(min_cuts),
                                       np.nanmax(max_cuts),
                                       num = 128))
            points = sorted(list(set(min_cuts + points1 + max_cuts)))
            
            for rep in self.unique_reps:
                
                # first point to catch an empty list
                # caused by uneven rep numbers
                try:
                    sub = self.df[(self.df[self.rep] == rep) &
                                  (self.df[self.x] == group)][self.y]
                    arr = np.array(sub)
                    
                    # remove nan or inf values which 
                    # could cause a kde ValueError
                    arr = arr[~(np.isnan(arr))]
                    kde = gaussian_kde(arr, bw_method=bw)
                    kde_points = kde.evaluate(points)
                    # kde_points = kde_points - np.nanmin(kde_points) #why?
                    
                    # use min and max to make the kde_points
                    # outside that dataset = 0
                    idx_min = min_cuts.index(arr.min())
                    idx_max = max_cuts.index(arr.max())
                    if idx_min > 0:
                        for p in range(idx_min):
                            kde_points[p] = 0
                    for idx in range(idx_max - len(max_cuts), 0):
                        if idx_max - len(max_cuts) != -1:
                            kde_points[idx+1] = 0
                    
                    # remove nan prior to combining arrays into dictionary
                    kde_wo_nan = self._interpolate_nan(kde_points)
                    points_wo_nan = self._interpolate_nan(points)
                    
                    # normalize each stripe's area to a constant
                    # so that they all have the same area when plotted
                    area = 30
                    kde_wo_nan = (area / sum(kde_wo_nan)) * kde_wo_nan
                    
                    norm_wy.append(kde_wo_nan)
                    px.append(points_wo_nan)
                except ValueError:
                    norm_wy.append([])
                    px.append(self._interpolate_nan(points))
            px = np.array(px)
            
            # print Scott's factor to the console to help users
            # choose alternative values for bw
            try:
                if bw == None:
                    scott = kde.scotts_factor()
                    print(f"Fitting KDE with Scott's Factor: {scott:.3f}")
            except UnboundLocalError:
                pass
            
            # catch the error when there is an empty list added to the dictionary
            length = max([len(e) for e in norm_wy])
            
            # rescale norm_wy for display purposes
            norm_wy = [a if len(a) > 0 else np.zeros(length) for a in norm_wy]
            norm_wy = np.array(norm_wy)
            norm_wy = np.cumsum(norm_wy, axis = 0)
            try:
                norm_wy = norm_wy / np.nanmax(norm_wy) # [0,1]
            except ValueError:
                print("Failed to normalize y values")
            
            # update the dictionary with the normalized data
            # and corresponding x points
            self.subgroup_dict[group]["norm_wy"] = norm_wy
            self.subgroup_dict[group]["px"] = px
    
    @staticmethod
    def _interpolate_nan(arr):
        """
        Interpolate NaN values in numpy array of x co-ordinates of each fitted
        kernel density estimator to prevent gaps in the stripes of each Violin
        SuperPlot

        Parameters
        ----------
        arr : numpy array
            array of x co-ordinates of a fitted kde

        Returns
        -------
        arr : TYPE
            array of x co-ordinates with interpolation for each NaN value
            if present

        """
        diffs = np.diff(arr, axis=0)
        median_val = np.nanmedian(diffs)
        nan_idx = np.where(np.isnan(arr))
        if nan_idx[0].size != 0:
            arr[nan_idx[0][0]] = arr[nan_idx[0][0] + 1] - median_val
        return arr
    
    def _single_subgroup_plot(self, group, axis_point, mid_df,
                              total_width, linewidth):
        """
        Plot a Violin SuperPlot for the given condition

        Parameters
        ----------
        group : string
            Categorical condition to be plotted on the x axis
        axis_point : integer
            The point on the x-axis over which the Violin SuperPlot will be
            centred
        mid_df : Pandas DataFrame
            Dataframe containing the middle values of each replicate
        total_width : float
            Half the width of each Violin SuperPlot
        linewidth : float
            Width value for the outlines of each Violin SuperPlot and the 
            summary statistics skeleton plot

        Returns
        -------
        None.

        """
        
        # select scatter size based on number of replicates
        scatter_sizes = [10, 8, 6, 4]
        if len(self.unique_reps) < 3:
            num = 0 
        elif len(self.unique_reps) > len(scatter_sizes):
            num = -1
        else:
            num = len(self.unique_reps) - 3
        scatter_size = scatter_sizes[num]
        
        norm_wy = self.subgroup_dict[group]["norm_wy"]
        px = self.subgroup_dict[group]["px"]
        right_sides = np.array([norm_wy[-1]*-1 + i*2 for i in norm_wy])
        
        # create array of 3 lines which denote the 3 replicates on the plot
        new_wy = []
        for i in range(len(px)):
            if i == 0:
                newline = np.append(norm_wy[-1]*-1,
                                    np.flipud(right_sides[i]))
            else:
                newline = np.append(right_sides[i-1],
                                    np.flipud(right_sides[i]))
            new_wy.append(newline)
        new_wy = np.array(new_wy)
        
        # use last array to plot the outline
        outline_y = np.append(px[-1], np.flipud(px[-1]))
        append_param = np.flipud(norm_wy[-1]) * -1
        outline_x = np.append(norm_wy[-1],
                              append_param)*total_width + axis_point
        
        # Temporary fix; find original source of the
        # bug and correct when time allows
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
            
            # check if _on_legend contains the rep
            if a in self._on_legend:
                lbl = ""
            else:
                lbl = a
                self._on_legend.append(a)
            
            # plot separating lines and stripes
            plt.plot(reshaped_y, reshaped_x, c="k",
                     linewidth=self.sep_linewidth)
            plt.fill(reshaped_y, reshaped_x, color=self.colours[i],
                     label=lbl, linewidth=self.sep_linewidth,)
            
            # get the mid_val each replicate and find it in reshaped_x
            # then get corresponding point in reshaped_x to plot the points
            if mid_val.size > 0: # account for empty mid_val
                arr = reshaped_x[np.logical_not(np.isnan(reshaped_x))]
                nearest = self._find_nearest(arr, mid_val[0])
                
                # find the indices of nearest in new_wy
                # there will be two because new_wy is a loop
                idx = np.where(reshaped_x == nearest)
                x_vals = reshaped_y[idx]
                x_val = x_vals[0] + ((x_vals[1] - x_vals[0]) / 2)
                plt.scatter(x_val, mid_val[0], facecolors=self.colours[i],
                            edgecolors="Black", linewidth=self.sep_linewidth,
                            zorder=10, marker="o", s=scatter_size)
        plt.plot(outline_x, outline_y, color="Black", linewidth=linewidth)
        
    def plot_subgroups(self, centre_val, middle_vals, error_bars, ylimits,
                       total_width, linewidth, show_stats, show_legend):
        """
        Plot all subgroups of the df attribute

        Parameters
        ----------
        centre_val : string
            Central measure used for the skeleton plot. Either mean or median
        middle_vals : string
            Central measure of each replicate. Either mean, median, or robust
            mean
        error_bars : string
            Method for displaying error bars in the skeleton plot. Either SEM
            for standard error of the mean, SD for standard deviation,
            or CI for 95% confidence intervals
        ylimits : string
            User-specified ylimits in the form (lower, upper) where lower and 
            upper are float values
        total_width : float
            Half the width of each Violin SuperPlot
        linewidth : float
            Width value for the outlines of each Violin SuperPlot and the 
            summary statistics skeleton plot
        show_stats : string
            Either "yes" or "no" to overlay the statistics on the plot

        Returns
        -------
        None.

        """
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
            
            # calculate the mean/median value for
            # all replicates of the variable
            sub = self.df[self.df[self.x] == a]
            
            # robust mean calculates mean using data
            # between the 2.5 and 97.5 percentiles
            if middle_vals == "robust":
                
                # loop through replicates in sub
                subs = []
                for rep in sub[self.rep].unique():
                    
                    # drop rows containing NaN values as
                    # they mess up the subsetting
                    s = sub[sub[self.rep] == rep].dropna()
                    lower = np.percentile(s[self.y], 2.5)
                    upper = np.percentile(s[self.y], 97.5)
                    s = s.query(f"{lower} <= {self.y} <= {upper}")
                    subs.append(s)
                sub = pd.concat(subs)
                middle_vals = "mean"
            
            # calculate mean from remaining data
            means = sub.groupby(self.rep,
                                as_index=False).agg({self.y : middle_vals})
            self._single_subgroup_plot(a, i*2, mid_df=means,
                                       total_width=total_width,
                                       linewidth=linewidth)
            
            # get mean or median line of the skeleton plot
            if centre_val == "mean":
                mid_val = means[self.y].mean()
            else:
                mid_val = means[self.y].median()
            
            # get error bars for the skeleton plot
            if error_bars == "SEM":
                sem = means[self.y].sem()
                upper = mid_val + sem
                lower = mid_val - sem
            elif error_bars == "SD":
                upper = mid_val + means[self.y].std()
                lower = mid_val - means[self.y].std()
            else:
                lower, upper = norm.interval(0.95, loc=means[self.y].mean(),
                                      scale=means[self.y].std())
            
            # plot horizontal lines across the column, centered on the tick
            plt.plot([i*2 - median_width / 1.5, i*2 + median_width / 1.5],
                         [mid_val, mid_val], lw=linewidth, color="k",
                         zorder=20)
            for b in [upper, lower]:
                plt.plot([i*2 - median_width / 4.5, i*2 + median_width / 4.5],
                         [b, b], lw=linewidth, color="k", zorder=20)
            
            # plot vertical lines connecting the limits
            plt.plot([i*2, i*2], [lower, upper], lw=linewidth, color="k",
                     zorder=20)
        
        # add legend
        if show_legend != "no":
            plt.legend(loc=1, bbox_to_anchor=(1.1,1.1))
        
        plt.xticks(ticks, lbls)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.tight_layout()
        if ylimits != "None" and show_stats != "yes":
            lims = (float(i) for i in ylimits.split(", "))
            plt.ylim(lims)
        
    @staticmethod
    def _find_nearest(array, value):
        """
        Helper function to find the value of an array nearest to the input
        value argument

        Parameters
        ----------
        array : numpy array
            array of x co-ordinates from the fitted kde
        value : float
            the middle value of 

        Returns
        -------
        float
            nearest value in array to the input value argument

        """
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]
    
    def get_statistics(self, centre_val="mean", paired="no",
                       on_plot="yes", ylimits="None"):
        """
        Determine appropriate statistics for the dataset, output statistics in
        txt file if there are 3 or more groups, and overlay on plot (optional).

        Parameters
        ----------
        centre_val : string, optional
            Central measure used for the skeleton plot. Either mean or median.
            The default is "mean".
        paired : string, optional
            Either "yes" or "no" if the data are paired.
            The default is "no".
        on_plot : string, optional
            Either "yes" or "no" to put overlay the statistics on the plot.
            The default is "yes".
        ylimits : string, optional
            User-specified ylimits in the form (lower, upper) where lower and 
            upper are float values. The default is "None".

        Returns
        -------
        None.

        """
        if centre_val == "robust":
            means = self.df.groupby([self.rep, self.x],
                                    as_index=False).agg({self.y : "mean"})
        else:
            means = self.df.groupby([self.rep, self.x],
                                    as_index=False).agg({self.y : centre_val})
        data = [list(means[means[self.x] == i][self.y]) for i in means[self.x].unique()]
        
        num_groups = len(self.subgroups)
        
        if num_groups > 2:
            # compute one-way ANOVA test results
            stat, p = f_oneway(*data)
            
            # use tukey to compare all groups with Bonferroni correction
            posthoc = sp.posthoc_tukey(means, self.y, self.x)
            print(f"One-way ANOVA P-value: {p:.3f}")
            print("Tukey posthoc tests conducted")
            
            # round p values to 3 decimal places in posthoc tests
            posthoc = posthoc.round(3)
            # save statistics to file
            posthoc.to_csv(f"posthoc_statistics_{self.y}.txt", sep="\t")
            print("Posthoc statistics saved to txt file")
        elif num_groups == 2:
            if paired == "no":
                # independent t-test
                stat, p = ttest_ind(data[0], data[1])
                if p < 0.0001:
                    print(f"Independent t-test P-value: {p:.2e}")
                else:
                    print(f"Independent t-test P-value: {p:.3f}")
            else:
                # paired t-test
                stat, p = ttest_rel(data[0], data[1])
                if p < 0.0001:
                    print(f"Paired t-test P-value: {p:.2e}")
                else:
                    print(f"Paired t-test P-value: {p:.3f}")
                    
        # plot statistics if only 2 or 3 groups
        if on_plot == "yes" and num_groups in [2, 3]:
            ax = plt.gca()
            low, high = ax.get_ylim()
            span = high - low
            increment = span * 0.03 # add high to get the new y value
            
            if num_groups == 2:
                x1, x2 = 0, 2
                y = increment + high
                h = y + increment
                plt.plot([x1, x1, x2, x2], [y, h, h, y], lw=1, c="k")
                plt.text((x1+x2)*.5, h, f"P = {p:.3f}", ha="center",
                         va="bottom", color="k", fontsize=8)
                plt.ylim((low, high+increment*10))
            elif num_groups == 3:
                labels = [i._text for i in ax.get_xticklabels()]
                pairs = ((0, 1), (1, 2), (0, 2))
                # increment = 3% of the range of the y-axis
                y = increment + high 
                text_loc = ["center", "center", "center"]
                
                for i,pair in enumerate(pairs):
                    # get posthoc statistic for each comparison
                    condition1, condition2 = [labels[i] for i in pair]
                    pval = posthoc.loc[condition1, condition2]
                    x1, x2 = [i * 2 for i in pair]
                    
                    # calculate values for lines and locating p-values on plot
                    h = y * 1.02
                    y += increment * 5
                    
                    # plot the posthoc p-values and lines
                    plt.plot([x1, x1, x2, x2], [h, y, y, h], lw=1, c="Black")
                    plt.text((x1+x2)/2, y, f"P = {pval:.3f}", ha=text_loc[i],
                             va="bottom", color="Black", fontsize=8)
                plt.ylim((low, low + span * 1.5))
            if ylimits != "None":
                lims = (float(i) for i in ylimits.split(", "))
                plt.ylim(lims)
            plt.tight_layout()
        