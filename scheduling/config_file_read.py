# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 11:42:11 2019

@author: tianan.lai
"""

import pandas as pd 
from collections import defaultdict


def get_config(filename="配置表.xlsx",WAREHOUSE_NAME='AU Warehouse'):
    config_map=defaultdict(list)
    config_df=pd.read_excel(filename)
    for index,row in config_df.iterrows():
        config_map[row['WAREHOUSE_NAME']].append((row['INDEX'],row['TIME_QUANTUM'],row['WORK_OVERTIME']))
    for k,v in config_map.items():
        config_map[k]=list(sorted(v,key=lambda x:x[0]))
    return config_map[WAREHOUSE_NAME]