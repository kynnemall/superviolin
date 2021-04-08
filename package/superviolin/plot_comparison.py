# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 14:51:42 2020

@author: Martin Kenny
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from plot import Superviolin

def generate_figures():
    # testing code
    # make ideal superplot
    os.chdir('templates')
    test = Superviolin(filename='demo_data.csv', data_format='tidy',
                     condition='drug', value='variable',
                     stats_on_plot='yes', paired_data="yes",
                     show_legend='yes')
    test.generate_plot()
    plt.ylabel('Spreading area ($\mu$$m^2$)')
    plt.tight_layout()
    # plt.close()
    # make Lord et al. SuperPlot
    # for x in range(6):
    #     if x != 1:
    #         test.x_vals[x] /= 2
    # test.beeswarm_plot(0.8,1)
    # test.get_statistics()
    # ax = plt.gca()
    # ax.legend_ = None
    # plt.ylabel('Spreading area ($\mu$$m^2$)')
    # SuperPlot with 6 replicates
    os.chdir(r'C:\Users\martinkenny\OneDrive - Royal College of Surgeons in Ireland\Documents\Writing\My papers\Superplot letter')
    df = pd.read_csv('20210126_6_replicates.csv')
    df = df[df['variable'] <= 55]
    test = Superviolin(condition='drug', value='variable', filename='',
                     replicate='rep', data_format='tidy', dataframe=df,
                     stats_on_plot='yes', paired_data="yes",
                     show_legend='yes')
    test.generate_plot()
    plt.ylabel('Spreading area ($\mu$$m^2$)')
    plt.tight_layout()
    
def generate_fakes():
    """
    

    Returns
    -------
    fake : Pandas DataFrame
        Fake data with specific mean and standard deviation

    """
    
    # tech_rep_n = [6, 36, 216, 1296]
    # bio_rep_n = [3, 6, 12, 24]
    tech_rep = 1296
    
    # create fake dataset
    variable = []
    replicate = []
    
    for bio_rep in range(1, 25):
        # generate new mean and SD for each biological replicate
        # get mean from normal distribution with mean 10 and SD 2
        # get SD from normal distribution with mean 5 and SD 2 or 3
        mean = np.random.normal(10, 1.5)
        sd = np.random.normal(2, 0.5)
        
        # use normal distribution with certain mean and SD
        # vary mean and SD for the biological replicates
            
        data = np.random.normal(mean, sd, tech_rep)
        variable.append(data)
        replicate.extend([bio_rep] * tech_rep)
    
    # concatenate list of arrays to a single array
    variable = np.concatenate(variable, axis=0)
    
    df = pd.DataFrame({'variable' : variable, 'condition' : [1] * len(variable),
                         'replicate' : replicate})
    
    # make fake data files
    sub_dfs = []
    data = {'bio/tech' : []}
    for bio_rep in [3,6,12,24]:
        for tech_rep in [6,36,216,1296]:
            sub = df[df['replicate'] <= bio_rep]
            reps = []
            for r in sub['replicate'].unique():
                sub_2 = sub[sub['replicate'] == r].reset_index()
                reps.append(sub_2.iloc[:tech_rep, :])
            reps = pd.concat(reps)
            data['bio/tech'].append((bio_rep, tech_rep))
            sub_dfs.append(reps)
            
    # change dir and save files
    print('saving data')
    os.chdir(r'C:\Users\martinkenny\OneDrive - Royal College of Surgeons in Ireland\Documents\Writing\My papers\Superplot letter\fake_data_grid')
    for data, bio_tech in zip(sub_dfs, data['bio/tech']):
        b = str(bio_tech[0]).zfill(2)
        r = str(bio_tech[1]).zfill(4)
        savename = f"fake_bio-reps-{b}_tech-reps-{r}.csv"
        data.to_csv(savename, index=False)
    
def make_superviolins():
    os.chdir(r'C:\Users\martinkenny\OneDrive - Royal College of Surgeons in Ireland\Documents\Writing\My papers\Superplot letter\fake_data_grid')
    files = [i for i in os.listdir() if i.endswith('csv')]
    for f in files:
        print(f)
        # reduce line thickness to 0.2
        test = Superviolin(f, 'tidy', value='variable', xlabel='', ylabel='',
                           cmap='tab20', ylimits= "-1, 25",
                           sep_linewidth=0.2)
        # define custom color map (24)
        from matplotlib.colors import rgb2hex
        cmap = plt.get_cmap('tab20')
        custom_cmap = [rgb2hex(cmap(i)) for i in range(cmap.N)] * 2
        test.colours = custom_cmap[:24]
        
        test.generate_plot()
        plt.tight_layout()
        # save svg
        savename = f.replace('csv', 'svg')
        plt.savefig(savename, dpi=600)
        # save png
        savename = f.replace('csv', 'png')
        plt.savefig(savename, dpi=600)
        plt.close()
    print(custom_cmap[:24])