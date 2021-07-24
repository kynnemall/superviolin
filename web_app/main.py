#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 16:21:59 2021

@author: martin
"""

import pandas as pd
import streamlit as st
from superviolin.plot import Superviolin

st.set_page_config(page_title="Violin SuperPlot Web App")

st.title("Official Violin SuperPlots Web App")
st.markdown("""
        This web app uses the _Superviolin_ Python package created as part of 
        the paper **Violin SuperPlots: Visualizing heterogeneity in large datasets** 
        to generate Violin SuperPlots based on your uploaded data. You can then download the
        resulting plot as an SVG or PNG file.
        """)

col1,col2 = st.beta_columns(2) 

# settings as radio buttons and text input
tidy = col1.radio("Choose data format", ("Tidy", "Untidy"))
suffix = col2.radio("Choose a file format", ("CSV", "Excel"))
condition = col1.text_input("Name of the conditions column in your data")
value = col1.text_input("Name of the value column in your data")
replicate = col1.text_input("Name of the replicate column in your data")
xlabel = col1.text_input("Text you want on the X axis")

mid_vals = col2.radio("Mean or median per replicate", ("Mean", "Median"))
centre_vals = col2.radio("Mean or median for overall statistics", ("Mean", "Median"))
error_bars = col2.radio("Choose format for error bars", ("SEM", "SD", "95% CI"))
ylabel = col2.text_input("Text you want on the Y axis")

uploaded_file = st.file_uploader("Upload a CSV or Excel file")

# process logic to make superviolin
if uploaded_file is not None:
    if suffix == "CSV":
        df = pd.read_csv(uploaded_file)
    else:
        if tidy == "Tidy":
            df = pd.read_excel(uploaded_file)
        else:
            pass
