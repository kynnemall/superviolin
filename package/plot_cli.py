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
        for l in lines:
            click.echo(l)
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

@click.group()
def cli():
    pass    

@cli.command('init', short_help = "Create args.txt in current directory")
def init():
    txt_data = pkgutil.get_data(__name__, "templates/args.txt").decode()
    click.echo(txt_data)    
    with open("args.txt", "w") as f:
        f.write(txt_data)
    click.echo('Created args.txt')

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
    click.echo(type(df))
    superplot(**d, dataframe = df)
    plt.show()
    
