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
import pandas as pd
import matplotlib.pyplot as plt
from appdirs import AppDirs
from superviolin.plot import Superplot

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
        k, v = l.replace('\n', '').split(": ")
        try:
            arg_dict[k] = float(v)
        except ValueError:
            if k == 'None':
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
        txt_data = pkgutil.get_data(__name__, "templates/demo_args.txt").decode()
        lines = txt_data.split('\n')
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
    _version = "0.9"
    dirs = AppDirs(_name, _author, _version)
    user_data_args = os.path.join(dirs.user_data_dir, "args.txt")
    if not os.path.exists(dirs.user_data_dir):
        os.makedirs(dirs.user_data_dir, mode=0o777)     
    txt_data = pkgutil.get_data(__name__, "templates/args.txt").decode()
    with open(user_data_args, "w") as f:
        f.write(txt_data)
    return user_data_args

@click.group()
def cli():
    pass

@cli.command('init', short_help="Create args.txt in current directory")
def init():
    user_data_args = make_user_data_dir()
    with open(user_data_args, "r") as default:
        txt_data = default.readlines()
        txt_lines = []
        for l in txt_data:
            if l != '\n':
                txt_lines.append(l)
            if not l.startswith('#'):
                txt_lines.append('\n')
        txt_data = ''.join(txt_lines)
    with open("args.txt", "w") as f:
        f.write(txt_data)
    click.echo('Created args.txt')
    click.echo('Modify args.txt with your preferences, then run "superviolin plot"')

@cli.command('plot', short_help="Generate Violin SuperPlot")
def make_superplot():
    d = get_args()
    if not d:
        click.echo("args.txt not found in current folder")
    else:
        violin = Superplot(**d)
        violin.generate_plot()
        plt.show()

@cli.command('demo', short_help="Make demo Violin SuperPlot")
def demo():
    d = get_args(demonstration=True)
    bytedata = pkgutil.get_data(__name__, "templates/demo_data.csv")
    df = pd.read_csv(io.BytesIO(bytedata))
    violin = Superplot(**d, dataframe=df)
    violin.generate_plot()
    plt.show()