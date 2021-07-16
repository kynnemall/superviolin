#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 18:27:08 2021

@author: martin
"""
from os import path
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
      name = "superviolin",
      py_modules = ["plot_cli", "plot"],      
      version = "1.0.0",
      url = "",
      description = "Python CLI to make Violin SuperPlots",
      long_description = long_description,
      long_description_content_type = "text/markdown",
      author = "Martin Kenny",
      author_email = "sideproject1892@gmail.com",
      maintainer = "Martin Kenny",
      maintainer_email = "sideproject1892@gmail.com",
      packages = find_packages(),
      entry_points = {
                      "console_scripts": ["superviolin=superviolin.plot_cli:cli"]
                      },
      python_requires = ">=3.6.2",
      install_requires = [
          "appdirs",
          "click",
          "matplotlib",
          "numpy",
          "pandas",
          "scipy",
          "xlrd",
          "openpyxl",
          "scikit-posthocs"
          ],
      package_data = {"" : ["demo_data.csv",
                            "args.txt",
                            "demo_args.txt",
                            "test.pkl"]
                      },
      classifiers = [
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          ],
      )
