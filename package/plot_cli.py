#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 9 13:49:42 2021

@author: Martin Kenny
"""

import io
import os
import click
import pkgutil
import pandas as pd
import matplotlib.pyplot as plt
from plot import superplot
from appdirs import AppDirs

def process_txt(txt):
    arg_dict = {}
    lines = [i.rstrip() for i in txt if not i.startswith("#")]
    lines = [i for i in lines if len(i) > 0]
    for l in lines:
        key_val = l.split(": ")
        try:
            arg_dict[key_val[0]] = float(key_val[1])
        except:
            if key_val[1] == 'None':
                arg_dict[key_val[0]] = None
            else:
                arg_dict[key_val[0]] = key_val[1]
    return arg_dict

def get_args(demo = False):
    if demo:
        txt_data = pkgutil.get_data(__name__, "templates/demo_args.txt").decode()
        lines = txt_data.split('\n')
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
    _name = "schoenplot"
    _author = "Martin Kenny"
    _version = "0.4"
    dirs = AppDirs(_name, _author, _version)
    user_data_args = os.path.join(dirs.user_data_dir, "args.txt")
    if not os.path.exists(dirs.user_data_dir):
        os.makedirs(dirs.user_data_dir, mode = 0o777)
    if not os.path.isfile(user_data_args):        
        txt_data = pkgutil.get_data(__name__, "templates/args.txt").decode()
        with open(user_data_args, "w") as f:
            f.write(txt_data)
    return user_data_args

@click.group()
def cli():
    pass    

@cli.command('init', short_help = "Create args.txt in current directory")
def init():
    user_data_args = make_user_data_dir()
    with open(user_data_args, "r") as default:
        txt_data = default.read()
    with open("args.txt", "w") as f:
        f.write(txt_data)
    click.echo('Created args.txt')
    click.echo('Modify args.txt with your preferences then run "schoenplot plot"')

@cli.command('plot', short_help = "Generate superplot")
def make_superplot():
    d = get_args()
    if not d:
        click.echo("args.txt not found in current folder")
    else:
        superplot(**d)
        plt.show()

@cli.command('demo', short_help = "Make demo superplot")
def demo():
    d = get_args(demo = True)
    bytedata = pkgutil.get_data(__name__, "templates/demo_data.csv")
    df = pd.read_csv(io.BytesIO(bytedata))
    superplot(**d, dataframe = df)
    plt.show()
    
@cli.command('prefs', short_help = "Change default arguments in args.txt template")
def prefs():
    user_data_args = make_user_data_dir()
    with open(user_data_args, "r") as default:
        txt_data = default.read()
    lines = txt_data.split('\n')
    arg_dict = process_txt(lines)
    for i,k in enumerate(arg_dict.keys()):
        if i > 4:
            old = f"{k}: {arg_dict[k]}"
            n = input(f"{old}, do you want to replace it?\n If not, just press enter\n")
            if len(n) == 0:
                click.echo(f"{k} unchanged")
            else:
                new = "f{k}: {n}"
                txt_data = txt_data.replace(old, new)
                click.echo(f"{arg_dict[k]} replaced with {n}")
    with open(user_data_args, "w") as f:
        f.write(txt_data)
    click.echo("\nNew settings successfully stored")
