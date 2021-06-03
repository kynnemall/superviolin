#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 9 13:49:42 2021

@author: Martin Kenny
"""

import io
import os
import pkgutil

import click
import unittest
import pandas as pd
import matplotlib.pyplot as plt
from appdirs import AppDirs
from superviolin import test_plot
from superviolin.plot import Superviolin

def process_txt(txt):
    """
    Process args.txt files to get pairs of arguments and values to be used
    for generating Violin SuperPlots

    Parameters
    ----------
    txt : list of strings
        Data from a text file that was read in line-by-line

    Returns
    -------
    arg_dict : dictionary
        Argument and argument value pairs

    """
    arg_dict = {}
    lines = [i.rstrip() for i in txt if not i.startswith("#")]
    lines = [i for i in lines if len(i) > 0]
    for l in lines:
        k, v = l.replace("\n", "").split(": ")
        try:
            arg_dict[k] = float(v)
        except ValueError:
            if k == "None":
                arg_dict[k] = None
            else:
                arg_dict[k] = v
    return arg_dict

def get_args(demonstration=False, preferences=False):
    """
    Get arguments from txt files depending on whether the data is
    for a demo of the package or creating a Violin SuperPlot from user
    data.

    Parameters
    ----------
    preferences : TYPE, optional
        DESCRIPTION. The default is False.
    demonstration : Boolean, optional
        If True, get arguments from demo_args.txt and generate a Violin
        SuperPlot based on the demo data included with this package.
        The default is False.

    Returns
    -------
    dictionary
        Argument and argument value pairs for instantiating a superplot class

    """
    if demonstration:
        txt_data = pkgutil.get_data(__name__, "res/demo_args.txt").decode()
        lines = txt_data.split("\n")
        arg_dict = process_txt(lines)
        return arg_dict
    elif preferences:
        user_data_args = make_user_data_dir()
        with open(user_data_args, "r") as f:
            lines = f.readlines()
        arg_dict = process_txt(lines)
        return arg_dict
    else:
        if "args.txt" not in os.listdir():
            return False
        else:
            with open("args.txt", "r") as f:
                lines = f.readlines()
            arg_dict = process_txt(lines)
            return arg_dict
    
def make_user_data_dir():
    """
    Creates a user directory to store args.txt from the package

    Returns
    -------
    user_data_args : string
        The path to the folder which is used to store the default args.txt
        file for ease-of-access.

    """
    _name = "superviolin"
    _author = "Martin Kenny"
    dirs = AppDirs(_name, _author)
    user_data_args = os.path.join(dirs.user_data_dir, "args.txt")
    if not os.path.exists(dirs.user_data_dir):
        os.makedirs(dirs.user_data_dir, mode=0o777)  
    txt_data = pkgutil.get_data(__name__, "res/args.txt").decode()
    with open(user_data_args, "w") as f:
        f.write(txt_data)
    return user_data_args

@click.group()
def cli():    
    pass

@cli.command("init", short_help="Create args.txt in current directory")
def init():
    """
    Creates args.txt file in the current directory

    Returns
    -------
    None.

    """
    
    
    user_data_args = make_user_data_dir()
    with open(user_data_args, "r") as default:
        txt_data = default.read()
        # txt_data = txt_data.replace('\n\n#', '\n#')
        txt_data = txt_data.replace('\n\n\n#', '\n#')
    with open("args.txt", "w") as f:
        f.write(txt_data)
    click.echo("Created args.txt")
    click.echo("Modify args.txt with your preferences, then run `superviolin plot`")

@cli.command("plot", short_help="Generate Violin SuperPlot")
def make_superplot():
    """
    Generates a Violin SuperPlot based on the args.txt file in the current
    directory

    Returns
    -------
    None.

    """
    
    d = get_args()
    if not d:
        click.echo("args.txt not found in current folder")
    else:
        violin = Superviolin(**d)
        violin.generate_plot()
        plt.show()

@cli.command("demo", short_help="Make demo Violin SuperPlot")
def demo():
    """
    Generates a Violin SuperPlot using the demo data file included in 
    the package

    Returns
    -------
    None.

    """
    
    d = get_args(demonstration=True)
    bytedata = pkgutil.get_data(__name__, "res/demo_data.csv")
    df = pd.read_csv(io.BytesIO(bytedata))
    violin = Superviolin(**d, dataframe=df)
    violin.generate_plot()
    plt.show()
    
@cli.command("test", short_help="Test the Superviolin class to ensure it is working")
def test():
    """
    Run tests using the package to ensure everything is working as expected
    
    Returns
    -------
    None.

    """
    suite = unittest.TestLoader().loadTestsFromModule(test_plot)
    unittest.TextTestRunner(verbosity=2).run(suite)
    