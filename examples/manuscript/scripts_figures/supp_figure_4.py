#!/usr/bin/env python

# __author__ = Firas S Midani
# __email__ = midani@bcm.edu

# Midani et al. (2020) Supplemntal Figure 4 is generated by this script 

import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style('whitegrid')

def read_csv(foo): return pd.read_csv(foo,sep='\t',header=0,index_col=0)

# read model predictions
split_df = './biolog/derived/split_gp_data.txt'
poold_df = './biolog/derived/pooled_by_isolate_gp_data.txt'
    
split = read_csv(split_df)
poold = read_csv(poold_df)

# read raw data
data = []
summ = []

for pid in ['CD2015_PM1-1','CD2015_PM1-2']:
    data_filename = './biolog/derived/{}.tsv'.format(pid)
    summ_filename = './biolog/summary/{}.txt'.format(pid)
    data.append(pd.read_csv(data_filename,sep='\t',header=0,index_col=0))
    summ.append(pd.read_csv(summ_filename,sep='\t',header=0,index_col=0))

df_data = pd.concat(data,axis=1)
df_summ = pd.concat(summ,axis=0)

df_data.index = df_data.iloc[:,0]
df_data.drop(['Time'],axis=1,inplace=True)
df_data.columns = list(df_summ.index.values)

# plotting and auxiliary functions

from scipy.stats import norm

def subsetDf(df,criteria):
    
    for k,v in criteria.items():
        if not isinstance(v,list): criteria[k] = [v]
    
    return df[df.isin(criteria).sum(1)==len(criteria)]

def getLatentFunction(df,order=0,add_noise=False):
    '''
    Get arrays for time, mean, lower and upper bounds of confidence interval. 

    Args:
    	df (pandas.DataFrame): in the format of gp_data from AMiGA, so columns must
    		include 'mu','mu1','Sigma','Sigma1','Noise'.
    	order (int): choose zero-order (0) or fist-order derivative (1).
    	add_noise (boolean): whether to include estimated noise to confidence intervals.
    '''

    time = df.Time.values
    
    if order==0:
        mu = df.mu.values
        Sigma = df.Sigma.values
        if add_noise: Sigma = Sigma + df.Noise.values
    else:
        mu = df.mu1.values
        Sigma = df.Sigma1.values
    
    confidence = 0.95
    alpha = 1-confidence
    z_value = 1-alpha/2
    scaler = norm.ppf(z_value)
    
    low = mu - scaler*np.sqrt(Sigma)
    upp = mu + scaler*np.sqrt(Sigma) 
    
    return time,mu,low,upp

def largeTickLabels(ax): [ii.set(fontsize=20) for ii in ax.get_xticklabels()+ax.get_yticklabels()]

def plot_model(df_pred,df_data,df_summ,criteria,fig_ax=None,plot_raw=False):
    
    # if user does not pass an axis object
    if fig_ax is None:
        fig,(ax0,ax1) = plt.subplots(2,1,figsize=[5,10],sharex=True)
    elif len(fig_ax[1])==2:
        fig,(ax0,ax1) = fig_ax
    else: 
        print('USER ERROR: axis must have size 2x1')
        return None

    fit = subsetDf(df_pred,criteria).sort_values(['Time']) # get predictions
    
    # plot growth function
    x,y,ymin,ymax = getLatentFunction(fit,order=0,add_noise=True)
    ax0.plot(x,y,color=(0,0,0,0.8),lw=5)
    ax0.fill_between(x,ymin,ymax,color=(0,0,0,0.075))
    
    # plot growth rate function
    x,y,ymin,ymax = getLatentFunction(fit,order=1)
    ax1.plot(x,y,color=(0,0,0,0.8),lw=5)
    ax1.fill_between(x,ymin,ymax,color=(0,0,0,0.075))
    
    if plot_raw:
        
        summ_idx = subsetDf(df_summ,criteria)
        data_idx = df_data.loc[:,summ_idx.index].iloc[1:,:]
        time = data_idx.index.values/3600
        data = data_idx.apply(np.log)
        data = data - data.iloc[0,:]
        data = data.values
        
        ax0.plot(time,data,color=(1,0,0,0.5),lw=2)
    
    largeTickLabels(ax0)
    largeTickLabels(ax1)

# plot
fig,axes = plt.subplots(2,3,figsize=[14,9],sharex=True,sharey=False)

criteria0 = {'Substrate':'L-Threonine', 'Isolate':'CD2015', 'PM':1}
criteria1 = {'Substrate':'D-Sorbitol', 'Isolate':'CD2015', 'PM':1}
criteria2 = {'Substrate':'D-Fructose', 'Isolate':'CD2015', 'PM':1}

plot_model(poold,df_data,df_summ,criteria0,plot_raw=True,fig_ax=(fig,axes[:,0]));
plot_model(poold,df_data,df_summ,criteria1,plot_raw=True,fig_ax=(fig,axes[:,1]));
plot_model(poold,df_data,df_summ,criteria2,plot_raw=True,fig_ax=(fig,axes[:,2]));

## adjust window limits
axes[0,0].set_xlim([-1,25])

[ax.set_ylim([-0.3,3.3]) for ax in axes[0,:]];
[ax.set_ylim([-0.4,0.8]) for ax in axes[1,:]];

## adjust tick labels
yticks0 = np.linspace(0,3,4)
yticks1 = np.linspace(-0.4,0.8,4)
yticklabels0 = ['{:.1f}'.format(ii) for ii in yticks0]

plt.setp(axes[0,0],xticks=np.linspace(0,24,4))

[plt.setp(ax,yticks=yticks0,yticklabels=yticklabels0) for ax in axes[0,:]];
[plt.setp(ax,yticks=yticks1) for ax in axes[1,:]];

[plt.setp(ax,yticklabels=[]) for ax in axes[0,1:]];
[plt.setp(ax,yticklabels=[]) for ax in axes[1,1:]];

## adjust tick label sizes
[largeTickLabels(ax) for ax in axes[0,:]];
[largeTickLabels(ax) for ax in axes[0,:]];

## adjust axes labels
[ax.set_xlabel('Time (hours)',fontsize=20) for ax in axes[1,:]];

axes[0,0].text(x=-0.3,y=0.5,transform=axes[0,0].transAxes,
               s='ln OD(t)',fontsize=20,rotation=90,va='center',ha='center')

axes[1,0].text(x=-0.3,y=0.5,transform=axes[1,0].transAxes,
               s=r'$\frac{\mathrm{d}}{\mathrm{dt}}$ ln OD(t)',fontsize=20,rotation=90,va='center',ha='center')

for ii,title in enumerate(['L-Threonine','D-Sorbitol','D-Fructose']):
    axes[0,ii].set_title(title,fontsize=20,y=1.05)
    
#[ax.xaxis.grid(False) for ax in np.ravel(axes)];
#[ax.yaxis.grid(False) for ax in np.ravel(axes)];

[[ax.spines[ii].set(lw=0) for ii in ['top','bottom','right','left']] for ax in np.ravel(axes)];

[ax.axhline(0,0,1,lw=2,color='k') for ax in np.ravel(axes)]
[ax.axvline(0,0,1,lw=2,color=(0,0,0,1),zorder=2) for ax in np.ravel(axes)]

# add panel letters
axes[0,0].text(transform=axes[0,0].transAxes,x=-0.05,y=1.15,ha='left',va='top',s='A',fontsize=30,fontweight='bold')
axes[0,1].text(transform=axes[0,1].transAxes,x=-0.05,y=1.15,ha='left',va='top',s='B',fontsize=30,fontweight='bold')
axes[0,2].text(transform=axes[0,2].transAxes,x=-0.05,y=1.15,ha='left',va='top',s='C',fontsize=30,fontweight='bold')

# save figure as PDF and convert to EPS
filename = 'Midani_AMiGA_Supp_Figure_4'
plt.savefig('./figures/{}.pdf'.format(filename),bbox_inches='tight')
