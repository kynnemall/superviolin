#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 16:21:59 2021

@author: martin
"""

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from superviolin.plot import Superviolin

st.set_page_config(page_title="Violin SuperPlot Web App")
st.set_option('deprecation.showPyplotGlobalUse', False)

st.title("Official Violin SuperPlot Web App")
st.markdown("""
        This web app uses the _Superviolin_ Python package created as part of 
        the paper **Violin SuperPlots: Visualizing heterogeneity in large datasets** 
        to generate Violin SuperPlots based on your uploaded data. You can then download the
        resulting plot as an SVG or PNG file.
        """)

col1,col2 = st.beta_columns(2)

# settings as radio buttons and text input
tidy = col2.radio("Choose data format", ("Tidy", "Untidy"))
suffix = col2.radio("Choose a file format", ("CSV", "Excel"))
condition = col1.text_input("Name of the conditions column in your data")
value = col1.text_input("Name of the value column in your data")
replicate = col1.text_input("Name of the replicate column in your data")
xlabel = col1.text_input("Label for the X axis")

mid_vals = col2.radio("Mean or median per replicate", ("Mean", "Median"))
centre_vals = col2.radio("Mean or median for overall statistics", ("Mean", "Median"))
error_bars = col2.radio("Choose format for error bars", ("SEM", "SD", "95% CI"))
ylabel = col1.text_input("Label for the Y axis")
ylims = col1.text_input("Min and max limits for Y axis", "None")

stats_on_plot = col2.radio("Show statistics on plot (only works for 2 conditions)",
                           ("Yes", "No"))
dpi = col1.text_input("DPI for saving the Violin SuperPlot", "1200")
save_format = col1.text_input("Figure save format", "svg")

uploaded_file = st.file_uploader("Upload a CSV or Excel file")

# process logic to make superviolin
if uploaded_file is not None:
    fname = datetime.now().strftime(
        "%Y%m%d_%H-%M-%S_ViolinSuperPlot"
        ) + f".{save_format}"
    save = col2.radio("Save figure", ("Yes", "No"))
    if suffix == "CSV":
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    if tidy == "Tidy":
        plot = Superviolin(dataframe=df, xlabel=xlabel,
                   condition=condition, value=value, replicate=replicate,
                   centre_val=centre_vals.lower(), ylabel=ylabel,
                   middle_vals=mid_vals.lower(), error_bars=error_bars,
                   stats_on_plot=stats_on_plot.lower(), dpi=int(dpi))
    else:
        # read multiple sheets in "untidy" format
        xl = pd.ExcelFile(uploaded_file)
        sheets = xl.sheet_names # replicates
        dfs = []
        for s in sheets:
            df = xl.parse(s)
            if not df.empty:
                df = df.melt(value_vars=df.columns.tolist(),
                             var_name=condition,
                             value_name=value)
                df[replicate] = s
                dfs.append(df)
        df = pd.concat(dfs)
        
        plot = Superviolin(dataframe=df,
                   condition=condition, value=value, replicate=replicate,
                   centre_val=centre_vals.lower(), xlabel=xlabel,
                   middle_vals=mid_vals.lower(), error_bars=error_bars,
                   ylabel=ylabel, stats_on_plot=stats_on_plot.lower(),
                   dpi=int(dpi))
    plot.generate_plot()
    if save == "Yes":
        plt.savefig(fname, dpi=int(dpi))
    st.pyplot()
    
    # download the plot and the statistics
    def download():
        pass
