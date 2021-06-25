# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 10:44:09 2021

@author: martinkenny
"""

import io
import pkgutil
import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from superviolin.plot import Superviolin
from superviolin import plot_cli

class TestingSuperplotMethods(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super(TestingSuperplotMethods, self).__init__(*args, **kwargs)
        
        # generate demo superplot
        arguments = plot_cli.get_args(demonstration=True)
        bytedata = pkgutil.get_data(__name__, "res/demo_data.csv")
        df = pd.read_csv(io.BytesIO(bytedata))
        self.superviolin = Superviolin(**arguments, dataframe=df)
        print("Plotting superviolin")
        self.superviolin.generate_plot()
        ax = plt.gca()
        
        # get data from plot and close it
        self.lines = []
        for a in ax.lines:
            arr = np.append(a.get_xdata(), a.get_ydata())
            self.lines.append(arr)
        plt.close()
    
    def test_plotted_lines_2_conditions(self):
        # load expected data
        bytedata = pkgutil.get_data(__name__, "res/test.pkl")
        bytelines = io.BytesIO(bytedata)
        real_lines = np.load(bytelines, allow_pickle=True)
        
        # compare generated data with expected data
        for a,b in zip(self.lines, real_lines):
            np.testing.assert_allclose(a, b)
        
if __name__ == "__main__":
    unittest.main()