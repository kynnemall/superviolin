#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 18:27:08 2021

@author: martin
"""

from setuptools import setup, find_packages

setup(
      name = "superviolin",
      version = 0.4,
      py_modules = ['plot_cli', 'plot'],
      url = "",
      description = "Python-based app to make superplots",
      author = "Martin Kenny",
      author_email = "mkenny5@tcd.ie",
      maintainer = "Martin Kenny",
      maintainer_email = "mkenny5@tcd.ie",
      packages = find_packages(),
      entry_points = {
                      'console_scripts': ['superviolin=plot_cli:cli']
                      },
      python_requires = ">=3.6",
      install_requires = [
          "appdirs",
          "click",
          "matplotlib",
          "numpy",
          "pandas",
          "scipy",
          "xlrd",
          "scikit-posthocs"
          ],
      package_data = {'' : ['demo_data.csv',
                            'args.txt',
                            'demo_args.txt']
                            },
      classifiers = [
          "Programming Language :: Python :: 3.6",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          ],
      )
