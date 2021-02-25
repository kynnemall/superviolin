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
from plot import superplot

def process_txt(txt):
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

def get_args(preferences=False, demonstration=False):
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
    _name = "superviolin"
    _author = "Martin Kenny"
    _version = "0.4"
    dirs = AppDirs(_name, _author, _version)
    user_data_args = os.path.join(dirs.user_data_dir, "args.txt")
    if not os.path.exists(dirs.user_data_dir):
        os.makedirs(dirs.user_data_dir, mode=0o777)
        click.echo("Making directory")
    if not os.path.isfile(user_data_args):        
        txt_data = pkgutil.get_data(__name__, "templates/args.txt").decode()
        with open(user_data_args, "w") as f:
            f.write(txt_data)
        click.echo("Making default args.txt file")
    return user_data_args

@click.group()
def cli():
    pass

@cli.command('init', short_help="Create args.txt in current directory")
def init():
    user_data_args = make_user_data_dir()
    click.echo(user_data_args)
    with open(user_data_args, "r") as default:
        txt_data = default.read()
    with open("args.txt", "w") as f:
        f.write(txt_data)
    click.echo('Created args.txt')
    click.echo('Modify args.txt with your preferences then run "superviolin plot"')

@cli.command('plot', short_help="Generate superplot")
def make_superplot():
    d = get_args()
    if not d:
        click.echo("args.txt not found in current folder")
    else:
        superplot(**d)
        plt.show()

@cli.command('demo', short_help="Make demo superplot")
def demo():
    d = get_args(demonstration=True)
    bytedata = pkgutil.get_data(__name__, "templates/demo_data.csv")
    df = pd.read_csv(io.BytesIO(bytedata))
    superplot(**d, dataframe=df)
    plt.show()
    
# extra lines are added to args.txt in templates folder when this command is used
# either fix or remove when released on PyPI 
#@cli.command('prefs', short_help="Change default arguments in args.txt template")
#def prefs():
#    user_data_args = make_user_data_dir()
#    with open(user_data_args, 'r+') as f:
#        click.echo(user_data_args)
#        lines = f.readlines()
#        arg_dict = get_args(preferences=True)
#        for i,l in enumerate(lines):
#            if not l.startswith('#') and ':' in l and 'REPLACE' not in l:
#                k, _ = l.split(': ')
#                old = f"{k}: {arg_dict[k]}"
#                n = input(f"{old}, do you want to replace it?\n If not, just press enter\n")
#                if not bool(n):
#                    click.echo(f"{k} unchanged")
#                else:
#                    new = f"{k}: {n}"
#                    click.echo(f"{arg_dict[k]} replaced with {n}")
#                    lines[i] = new
#        f.seek(0)
#        txt = ''.join(lines)
#        f.write(txt)
#    click.echo("\nNew settings successfully stored")
