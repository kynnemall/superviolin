#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 16:21:59 2021

@author: martin
"""

import re
import scipy
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from superviolin.plot import Superviolin
from matplotlib import rcParams as params
from streamlit_extras.dataframe_explorer import dataframe_explorer
st.set_page_config(page_title="Violin SuperPlot Web App",
                   page_icon="violin",
                   layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)

# hide menu from app users
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

st.markdown("""<div style="padding: 20px; border-radius: 5px;">
  <h2 style="font-size: 36px; color: #333; margin-bottom: 10px;">Visualize large datasets with ease using our web app!</h2>
  <p style="font-size: 20px; color: #555; line-height: 1.5; margin-bottom: 20px;">Powered by the Superviolin Python package, our app makes it easy to create beautiful and informative Violin SuperPlots described in our editorial <a href='https://www.molbiolcell.org/doi/10.1091/mbc.E21-03-0130'><strong>Violin SuperPlots: Visualizing heterogeneity in large datasets</strong></a>.</p>
  <p style="font-size: 20px; color: #555; line-height: 1.5; margin-bottom: 20px;">Simply upload your data, specify the relevant columns, and download your custom plots in SVG or PNG format.</p>
  <p style="font-size: 20px; color: #555; line-height: 1.5; margin-bottom: 20px;">With many options to customize the appearance, layout, and quality of your Violin SuperPlots, you can experiment with different settings which automatically update the plot as you go to find the perfect visualization for your data. Plus, section 6 of the <a href='https://github.com/kynnemall/superviolin/blob/master/documentation.pdf'><strong>documentation</strong></a> includes helpful tips for customizing the plot appearance and labeling your axes with sub/superscripts and Greek letters.</p>
  <p style="font-size: 20px; color: #555; line-height: 1.5; margin-bottom: 20px;">Try it out now and take your data visualization to the next level!</p>
</div>""", unsafe_allow_html=True)

with st.sidebar.expander("Upload data (required)"):

    # settings as radio buttons and text input
    tidy = st.radio("Choose data format", ("Tidy", "Untidy"))
    st.markdown('Examples of [**tidy**](https://github.com/kynnemall/superviolin/blob/master/web_app/tidy_example.png) and [**untidy**](https://github.com/kynnemall/superviolin/blob/master/web_app/untidy_example.png) data formats')
    suffix = st.radio("Choose a file format", ("CSV", "Excel"))
    condition = st.text_input("Name of the conditions column in your data")
    value = st.text_input("Name of the value column in your data")
    replicate = st.text_input("Name of the replicate column in your data")

    # get user data file
    uploaded_file = st.file_uploader("Upload a CSV or Excel file")

# optional settings
with st.sidebar.expander("Violin SuperPlot formatting"):
    order = st.text_input("Order of variables as they appear on the X axis (separate by comma and whitespace)",
                            "None")
    xlabel = st.text_input("Label for the X axis")
    ylabel = st.text_input("Label for the Y axis")
    cmap = st.selectbox("Choose a colour map for the replicates",
                        ("Pastel1", "Pastel2", "Paired", "Accent", "Dark2",
                        "Set1", "Set2", "Set3", "tab10", "tab20", "tab20b",
                        "tab20c"))
    st.markdown("[**More colourmap options**](https://matplotlib.org/stable/gallery/color/colormap_reference.html)")
    
    min_y = 0
    max_y = 1
    step = max_y / 200
    values = (0, 1)
    ylims = st.text_input("Min and max limits for Y axis (separate by comma and whitespace)", "None")
    
    bw = st.slider("BW value for smoothing the outlines", min_value=0.5,
                               max_value=1., value=0., step=0.05)
    dpi = st.text_input("DPI for saving the Violin SuperPlot", "1200")
    mid_vals = st.radio("Mean or median per replicate", ("Mean", "Median"))
    centre_vals = st.radio("Mean or median for overall statistics", ("Mean", "Median"))
    error_bars = st.radio("Choose format for error bars", ("SEM", "SD", "95% CI"))
    paired = st.radio("Paired data", ("Yes", "No"))
    stats_on_plot = st.radio("Show statistics on plot (only works for 2 conditions)",
                               ("Yes", "No"))
    
with st.sidebar.expander("General plot formatting"):
    violin_width = st.slider("Violin width", min_value=0.5,
                               max_value=1., value=0.8, step=0.05)
    violin_sep_lw = st.slider("Violin separating line width", min_value=0.1,
                               max_value=1.5, value=0.5, step=0.1)
    xtick_lbl_size = st.slider("X tick label size", min_value=0,
                               max_value=20, value=8, step=1)
    ytick_lbl_size = st.slider("Y tick label size", min_value=0,
                               max_value=20, value=8, step=1)
    axes_lbl_size = st.slider("Axes label size", min_value=0,
                               max_value=20, value=9, step=1)
    axes_lw = st.slider("Axes line width", min_value=0.2,
                               max_value=2., value=0.8, step=0.2)
    rotate_xticks = st.slider("X-tick rotation", value=0, min_value=0,
                              max_value=90, step=5)
    log_scale = st.checkbox('Log scale for Y axis')
    params["xtick.labelsize"] = xtick_lbl_size
    params["ytick.labelsize"] = ytick_lbl_size
    params["axes.labelsize"] = axes_lbl_size
    params["axes.linewidth"] = axes_lw
    params["xtick.minor.width"] = axes_lw / 2
    params["ytick.minor.width"] = axes_lw / 2
    params["xtick.major.width"] = axes_lw
    params["ytick.major.width"] = axes_lw

# include publication stats
with st.sidebar:
    st.markdown('Dimensions')
    st.components.v1.html('<span class="__dimensions_badge_embed__" data-doi="10.1091/mbc.e21-03-0130" data-legend="never"></span><script async src="https://badge.dimensions.ai/badge.js" charset="utf-8"></script>')

@st.cache_data
def read_data(fname, ending, tidy, condition, value, replicate):
    if ending == "CSV":
        df = pd.read_csv(fname)
    else:
        df = pd.read_excel(fname)
    assert condition in df.columns, st.markdown('Condition column not found in data; Are you sure you typed it correctly?')
    assert value in df.columns, st.markdown('Value column not found; Are you sure you typed it correctly?')
    assert replicate in df.columns, st.markdown('Replicate column not found; Are you sure you typed it correctly?')
        
    if tidy != "Tidy":
        # read multiple sheets in "untidy" format
        xl = pd.ExcelFile(fname)
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
    return df
    
# process logic to make superviolin
if uploaded_file is not None:
    df = read_data(uploaded_file, suffix, tidy, condition, value, replicate)

    with st.expander('Filter data (optional)'):
        st.markdown('<ul><li>Select a column from the selectbox below</li><li>If the variable is numeric, choose the upper and lower limits</li><li>If the variable is categorical, choose categories to keep</li></ul>',
                    unsafe_allow_html=True)
        fdf = dataframe_explorer(df)
    
    if bw == 0:
        bw = "None"
    if stats_on_plot == "Yes":
        show_stats = True
    else:
        show_stats = False
    plot = Superviolin(dataframe=fdf, condition=condition, value=value,
                       replicate=replicate, centre_val=centre_vals.lower(),
                       xlabel=xlabel, middle_vals=mid_vals.lower(),
                       error_bars=error_bars, ylabel=ylabel, bw=bw,
                       stats_on_plot=stats_on_plot.lower(), dpi=int(dpi),
                       paired_data=paired.lower(), return_stats=True,
                       cmap=cmap, order=order, ylimits=ylims,
                       sep_linewidth=violin_sep_lw, total_width=violin_width)
    plot.get_kde_data(plot.bw)
    plot.plot_subgroups(plot.centre_val, plot.middle_vals,
                        plot.error_bars, plot.ylimits,
                        plot.total_width, plot.linewidth,
                        plot.stats_on_plot, plot.show_legend)
    plt.xticks(rotation=rotate_xticks)
    if log_scale:
        plt.yscale('log')
    plt.savefig("ViolinSuperPlot.png", dpi=int(dpi))
    plt.savefig("ViolinSuperPlot.svg", dpi=int(dpi))
    st.image("ViolinSuperPlot.png", caption="Your Violin SuperPlot",
                 width=600)
    
    col1, col2 = st.sidebar.columns(2)
    with open("ViolinSuperPlot.svg", "rb") as f:
        fname = datetime.now().strftime("%Y%m%d_%H-%M-%S_ViolinSuperPlot.svg")
        col1.download_button("Download SVG", data=f, file_name=fname)
    with open("ViolinSuperPlot.png", "rb") as f:
        fname = datetime.now().strftime("%Y%m%d_%H-%M-%S_ViolinSuperPlot.png")
        col2.download_button("Download PNG", data=f, file_name=fname)
    
    # show statistics
    try:
        p, info = plot.get_statistics(plot.centre_val, plot.paired,
                                      plot.stats_on_plot, plot.ylimits,
                                      plot.return_stats)
        if len(plot.subgroups) == 2:
            if paired == "yes":
                st.write(f"Paired t-test p-value {p:.3f}")
            else:
                st.write(f"Unpaired t-test p-value {p:.3f}")
        else:
            st.markdown(f"<p><em>One-way ANOVA p-value <strong>{p:.3f}<strong></em><br><br>Table of Tukey posthoc statistics:</p>",
                        unsafe_allow_html=True)
            st.table(info)
            fname = f"posthoc_statistics_{value}.txt"
            try:
                with open(fname, "rb") as f:
                    st.sidebar.download_button("Download posthoc statistics",
                                               data=f, file_name=fname)
            except:
                pass
    except:
        st.write("Error calculating statistics")
    st.sidebar.markdown("**Please cite the editorial if using this web app to generate figures for publication**")
