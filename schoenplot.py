#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 9 13:49:42 2021

@author: Martin Kenny
"""

import os
import click
import matplotlib.pyplot as plt
from plot import superplot

def get_args():
    if "args.txt" not in os.listdir():
        print("args.txt not found in current folder")
    else:
        arg_dict = {}
        with open("args.txt", "r") as f:
            lines = f.readlines()
            lines = [i.rstrip() for i in lines if not i.startswith("#")]
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

@click.command()
def make_superplot():
    d = get_args()
    superplot(**d)
    plt.show()

if __name__ == "__main__":
    make_superplot()
