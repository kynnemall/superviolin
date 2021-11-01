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

st.set_page_config(page_title="Violin SuperPlot Web App", page_icon="violin",
                   layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)

# hide menu from app users
# st.markdown(""" <style>
# #MainMenu {visibility: hidden;}
# footer {visibility: hidden;}
# </style> """, unsafe_allow_html=True)

st.title("Official Violin SuperPlot Web App")
st.markdown("""
        <p style='text-align: justify'>This web app uses the Superviolin Python package created as part of 
        the editorial <a href='https://www.molbiolcell.org/doi/10.1091/mbc.E21-03-0130'><strong>Violin SuperPlots: Visualizing heterogeneity in large datasets</strong></a> 
        to generate Violin SuperPlots from user-supplied data, customize as you like, and download them
        in SVG or PNG format.<br>
        This web app works similarly to the Python package and uses input similar to those described in section 3 of the <a href='https://github.com/kynnemall/superviolin/blob/master/documentation.pdf'><strong>documentation</strong></a>.
        Please specify:
        <ul><li>The file format 
        (<a href='https://github.com/kynnemall/superviolin/blob/master/web_app/tidy_example.png'>tidy</a> or <a href='https://github.com/kynnemall/superviolin/blob/master/web_app/untidy_example.png'>untidy</a>)</li> 
        <li>the columns in your data</li><li>and whether your data is in the tidy format or not. 
        <em>If your data is in the untidy format, please provide column names so the app can process your data.</em></li>
        Any adjustments you make to the settings will be applied automatically. 
        Issues can be reported to Martin on <a href='(https://twitter.com/MartinPlatele'>Twitter</a> via direct message
        </p>""", unsafe_allow_html=True)
        
        
with st.sidebar.expander("Required input"):

    # settings as radio buttons and text input
    tidy = st.radio("Choose data format", ("Tidy", "Untidy"))
    suffix = st.radio("Choose a file format", ("CSV", "Excel"))
    condition = st.text_input("Name of the conditions column in your data")
    value = st.text_input("Name of the value column in your data")
    replicate = st.text_input("Name of the replicate column in your data")

    # get user data file
    uploaded_file = st.file_uploader("Upload a CSV or Excel file")

# optional settings
with st.sidebar.expander("Violin SuperPlot formatting (edit at any time)"):
    order = st.text_input("Order of variables as they appear on the X axis (separate by comma and whitespace)",
                            "None")
    xlabel = st.text_input("Label for the X axis")
    ylabel = st.text_input("Label for the Y axis")
    cmap = st.text_input("Choose a colour map for the replicates", "Set2")
    ylims = st.text_input("Min and max limits for Y axis (separate by comma and whitespace)", "None")
    bw = st.text_input("BW value for smoothing the outlines (decimal between 0 and 1, or None)", "None")
    dpi = st.text_input("DPI for saving the Violin SuperPlot", "1200")
    mid_vals = st.radio("Mean or median per replicate", ("Mean", "Median"))
    centre_vals = st.radio("Mean or median for overall statistics", ("Mean", "Median"))
    error_bars = st.radio("Choose format for error bars", ("SEM", "SD", "95% CI"))
    st.markdown("[**More colourmap options**](https://matplotlib.org/stable/gallery/color/colormap_reference.html)")
    paired = st.radio("Paired data", ("Yes", "No"))
    stats_on_plot = st.radio("Show statistics on plot (only works for 2 conditions)",
                               ("Yes", "No"))
    
with st.sidebar.expander("General plot formatting"):
    pass

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
                       paired_data=paired.lower(), return_stats=True,
                       cmap=cmap, order=order, ylimits=ylims)
    p, info = plot.generate_plot()
    plt.savefig("ViolinSuperPlot.png", dpi=int(dpi))
    plt.savefig("ViolinSuperPlot.svg", dpi=int(dpi))
    st.pyplot()
    
    # show statistics
    if len(plot.subgroups) == 2:
        if paired == "yes":
            st.write(f"Paired t-test p-value {p:.3f}")
        else:
            st.write(f"Unpaired t-test p-value {p:.3f}")
    else:
        st.write(f"One-way ANOVA p-value {p:.3f}; Table of Tukey posthoc statistics:")
        st.table(info)
    
    # st.markdown("__Please cite our editorial if you use a Violin SuperPlot in your work__")
    with open("ViolinSuperPlot.svg", "rb") as f:
        fname = datetime.now().strftime("%Y%m%d_%H-%M-%S_ViolinSuperPlot.svg")
        st.download_button("Download SVG", data=f, file_name=fname)
    with open("ViolinSuperPlot.png", "rb") as f:
        fname = datetime.now().strftime("%Y%m%d_%H-%M-%S_ViolinSuperPlot.png")
        st.download_button("Download PNG", data=f, file_name=fname)
