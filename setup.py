#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 18:27:08 2021

@author: martin
"""

from setuptools import setup

setup(
      name = "schoenplot",
      version = 0.4,
      url = "",
      project_urls = "",
      description = "Python-based app to make superplots",
      author = "Martin Kenny",
      maintainer = "Martin Kenny",
      maintainer_email = "mkenny5@tcd.ie",
      license = "BSD",
      entry_points = {
                      'console_scripts': ['schoenplot = schoenplot:main']
                      },
      python_requires = ">=3.1",
      install_requires = ["matplotlib", "numpy", "pandas", "scipy", "click"]
      )