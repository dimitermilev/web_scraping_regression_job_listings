import pandas as pd
import numpy as np
import sys
import re
import os
import json
import time

def initial_data_clean(jobs_data):
    '''Initial deduplication, dropping blanks, discarding part time and lab scientists'''
    
    '''Add job id variable for easy identification'''
    jobid = re.compile(r'(\d{10}$)')
    regmatch = np.vectorize(lambda x: jobid.search(x).group(1))
    jobs_data['job_id'] = regmatch(jobs_data.url.values)
    print("Before deduplication: ", raw_read.shape)
    jobs_data = jobs_data.drop_duplicates(['job_id'])
    print("After deduplication, before blanks and ineligibles: ", jobs_data.shape)
    
    '''Drop records with blanks and duplicates'''
    df = jobs_data[jobs_data['name'] !='']
    df = df.dropna(subset=['name'])
    
    '''Remove medical scientists'''
    df = df[df['occupationalCategory'] != "['19-1042.00', 'Medical Scientists, Except Epidemiologists']"]
    
    '''Keep only full-time positions'''
    df = df[df['employmentType'] == 'FULL_TIME']
    print("After blanks and ineligibles, before salary: ", df.shape)
    
    '''Remove records without salary information'''
    df = df.dropna(subset=['estimatedSalary_value_minValue'])
    print("After salary requirement: ", df.shape)
    
    '''Extract information from company details free text'''
    str_to_cols = []
    for i in range(df.shape[0]):
    
        '''Parse information using regex'''
        try:
            string = df.iloc[i]['company_details']
            pattern = re.compile(".+(?=\n)")
            res = pattern.findall(string)
            
            '''Create dictionary with company details information and job id'''
            info_dict = {}
            info_dict['job_id'] = df.iloc[i]['job_id']
            for item in res:
                if item[0:12] == 'Headquarters':
                    info_dict[item[0:12]] = item[12:]
                elif item[0:4] == 'Size':
                    info_dict[item[0:4]] = item[4:]
                elif item[0:7] == 'Founded':
                    info_dict[item[0:7]] = item[7:]        
                elif item[0:4] == 'Type':
                    info_dict[item[0:4]] = item[4:]
                elif item[0:8] == 'Industry':
                    info_dict[item[0:8]] = item[8:]
                elif item[0:6] == 'Sector':
                    info_dict[item[0:6]] = item[6:]
                elif item[0:7] == 'Revenue':
                    info_dict[item[0:7]] = item[7:]
            str_to_cols.append(info_dict)
        except:
            pass
    
    '''Merge main jobs df with job deails df'''
    df_details = pd.DataFrame(str_to_cols)
    res_df = pd.merge(df, df_details, on=['job_id'], how='left')
    return res_df