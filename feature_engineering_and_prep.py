import pandas as pd
import numpy as np
import sys
import re
import os
import json
import time
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import patsy
import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline

def impute_blanks_remove_outliers(df):
    '''Remove outliers'''
    high_cutoff = int(np.ceil(np.percentile([s for s in df['salaryMidpoint'].tolist()], 99.5)))  
    low_cutoff = int(np.ceil(np.percentile([s for s in df['salaryMidpoint'].tolist()], 0.5)))     
    df = df[df['salaryMidpoint']>=low_cutoff]
    '''Median impute missing values for benefits, ceo approval, overall approval, and work life balance'''
    df['benefits_ratings'] = df['benefits_ratings'].fillna(df['benefits_ratings'].median())
    df['ceo_approve'] = df['ceo_approve'].fillna(df['ceo_approve'].median())
    df['Overall'] = df['Overall'].fillna(df['Overall'].median())
    df['WorkLifeBalance'] = df['WorkLifeBalance'].fillna(df['WorkLifeBalance'].median())
    return df

def collinearity_check(df, var_list):
    df_smaller = df[var_list]
    plt.figure(figsize=(16, 8))
    sns.heatmap(df_smaller.corr(), cmap="seismic", annot=True, vmin=-1, vmax=1)
    sns.pairplot(df_smaller, height=1.2, aspect=1.5)
    return

def feature_engineer_vars(df, var_list):
    '''Feature engineer additional analysis fields: dummy variables, polynomial terms, interaction terms'''
    '''Categorical dummy variables'''
    df = df[var_list]
    df = pd.get_dummies(df)
    df = df.dropna()

    '''Polynomial variables'''
    df['Overall2'] = df['Overall'] ** 2
    df['cost_index2'] = df['cost_index'] ** 2

    '''Interaction terms'''
    def topskill(x):    
        return (x['machine'] + x['bigdata'] +  x['prgrm']) * 2        
    df['topskill'] = df.apply(topskill, axis=1)
    return df