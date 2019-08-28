# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 11:42:11 2019

@author: tianan.lai
"""

import pandas as pd 
from collections import defaultdict

import os 

def get_config(filename="config.xlsx",warehouse_name='AU_Warehouse'):
    config_map=defaultdict(list)
    path=os.path.join(os.getcwd(),filename)
    try:
        config_df=pd.read_excel(path)
    except Exception as e:
        raise Exception(("%s配置文件不存在"%warehouse_name)+str(e))
    for index,row in config_df.iterrows():
        config_map[row['WAREHOUSE_NAME']].append((row['INDEX'],row['TIME_QUANTUM'],row['WORK_OVERTIME']))
    for k,v in config_map.items():
        config_map[k]=list(sorted(v,key=lambda x:x[0]))
        
    if len(config_map[warehouse_name])==0:
        print(123)
        raise Exception("配置文件不存在指定的仓库%s"%warehouse_name)
        
    return config_map[warehouse_name]

