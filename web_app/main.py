#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 16:21:59 2021

@author: martin
"""

import base64
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
        the editorial [**Violin SuperPlots: Visualizing heterogeneity in large datasets**](https://www.molbiolcell.org/doi/10.1091/mbc.E21-03-0130) 
        to generate Violin SuperPlots based on your uploaded data. You can then download the
        resulting plot in SVG or PNG format.

        This web app works similarly to the Python package and uses input similar to those described in section 3 of the [**documentation**](https://github.com/kynnemall/superviolin/blob/master/documentation.pdf)
        """)

col1,col2 = st.beta_columns(2)

# settings as radio buttons and text input
tidy = col2.radio("Choose data format", ("Tidy", "Untidy"))
suffix = col2.radio("Choose a file format", ("CSV", "Excel"))
condition = col1.text_input("Name of the conditions column in your data")
value = col1.text_input("Name of the value column in your data")
replicate = col1.text_input("Name of the replicate column in your data")
order = col1.text_input("Order of the variables as they should appear on the X axis\nseparated by a comma and a single space",
                        "None")
xlabel = col1.text_input("Label for the X axis")

mid_vals = col2.radio("Mean or median per replicate", ("Mean", "Median"))
centre_vals = col2.radio("Mean or median for overall statistics", ("Mean", "Median"))
error_bars = col2.radio("Choose format for error bars", ("SEM", "SD", "95% CI"))
ylabel = col1.text_input("Label for the Y axis")
cmap = col1.text_input("Choose a colour map for the replicates", "Set2")
ylims = col1.text_input("Min and max limits for Y axis", "None")
bw = col1.text_input("BW value for smoothing the outlines decimal between 0 and 1, or None)", "None")

paired = col2.radio("Paired data", ("Yes", "No"))
stats_on_plot = col2.radio("Show statistics on plot (only works for 2 conditions)",
                           ("Yes", "No"))
dpi = col1.text_input("DPI for saving the Violin SuperPlot", "1200")
save_format = col2.radio("Figure save format", ("svg", "png"))

uploaded_file = st.file_uploader("Upload a CSV or Excel file")

# process logic to make superviolin
if uploaded_file is not None:
    if suffix == "CSV":
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    if tidy != "Tidy":
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
        
    if bw != "None":
        bw = float(bw)
    if stats_on_plot == "Yes":
        show_stats = True
    else:
        show_stats = False
    plot = Superviolin(dataframe=df, condition=condition, value=value,
                       replicate=replicate, centre_val=centre_vals.lower(),
                       xlabel=xlabel, middle_vals=mid_vals.lower(),
                       error_bars=error_bars, ylabel=ylabel, bw=bw,
                       stats_on_plot=stats_on_plot.lower(), dpi=int(dpi),
                       paired_data=paired.lower(), return_stats=show_stats,
                       cmap=cmap, order=order)
    p, info = plot.generate_plot()
    plt.savefig(f"ViolinSuperPlot.{save_format}", dpi=int(dpi))
    st.pyplot()
    
    # show statistics
    if len(plot.subgroups) == 2:
        if paired == "yes":
            st.write(f"Paired t-test p-value {p:.3f}")
        else:
            st.write(f"Unpaired t-test p-value {p:.3f}")
    else:
        st.write(f"One-way ANOVA p-value {p:.3f}. Table of Tukey posthoc statistics")
        st.table(info)
    
    # download the plot
    def download():
        time = datetime.now().strftime("%Y%m%d_%H-%M-%S_ViolinSuperPlot")
        fname = f"{time}.{save_format}"
        with open(f"ViolinSuperPlot.{save_format}", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        ref = f'<a href="data:application/octet-stream;base64,{b64}" download={fname}>Download Violin SuperPlot</a>'
        return ref
    st.markdown(download(), unsafe_allow_html=True)
