# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 14:37:54 2019

@author: tianan.lai
"""
from pulp import LpProblem,LpMinimize,LpVariable,LpStatus,value
import pulp

from  config_file_read  import get_config
import pandas as pd 
import numpy as np 

import sys,argparse

#assert order_sum+wait_pack>=va*2,"数据量太小,本程序不支持,请人工处理"

def train_model(warehouse_config_time,current_TIME_QUANTUM,order_sum,wait_pack,p_location,va,vb):
    upBound_person=300
    index=-1
    for i,TIME_QUANTUM,label in warehouse_config_time:
        if TIME_QUANTUM==current_TIME_QUANTUM:
            index=i
            break
        
#    assert index!=-1,"当前时间段在配置中找不到"
    
    warehouse_config_time=[e if e[0]>=index else (e[0],e[1],-1) for e in warehouse_config_time]
    
    Xa=[LpVariable("a%s"%(e[0]), lowBound=0,upBound=upBound_person,cat=pulp.LpInteger) for e in warehouse_config_time]
    
    Xb=[LpVariable("b%s"%(e[0]), lowBound=0,upBound=upBound_person,cat=pulp.LpInteger) for e in warehouse_config_time]
    
    
    ###待打包量
    Xs=[LpVariable("s%s"%(e[0]), lowBound=0) for i,e in enumerate(warehouse_config_time)]
    
    opponit_person= LpVariable("opponit_person", lowBound=0,upBound=upBound_person,cat=pulp.LpInteger)
    
    sum_=LpVariable("sum_time", lowBound=0 ,cat=pulp.LpInteger)
    
    z =opponit_person
    prob = LpProblem('orderperson', LpMinimize)
    prob += z
    
    sum_a=0
    for e in Xa:
        sum_a+=e*va
    sum_b=0
    for e in Xb:
        sum_b+=e*vb
    prob +=sum_a>=order_sum
    prob +=sum_b>=order_sum+wait_pack
    que_restrain_index=[e[0] for e in warehouse_config_time if e[2]==0]
    que_finish_index=[e[0] for e in warehouse_config_time if e[2]!=0]
    Xs=[]
    for e in que_finish_index:
        Xs.append((e,LpVariable("s%s"%(e), lowBound=0)))
    for index,e in enumerate(que_restrain_index):
        if index==len(que_restrain_index)-1:
            Xs.append((e,LpVariable("s%s"%(e), lowBound=-vb, upBound=0)))
        else:
            Xs.append((e,LpVariable("s%s"%(e), lowBound=-vb)))
    Xs=[e[1] for e in sorted(Xs,key=lambda x:x[0])]
    for i in que_finish_index:
        prob +=Xa[i]==0
        prob +=Xb[i]==0
        prob +=Xs[i]==0
        
    for index,i in enumerate(que_restrain_index):
        prob +=Xa[i]+Xb[i]<=opponit_person
        prob +=Xb[i]<=p_location
        if index<len(que_restrain_index)-1:
            prob +=Xa[que_restrain_index[index]]>=Xa[que_restrain_index[index+1]]
        if index==0:
            prob +=Xs[i]==wait_pack-Xb[i]*vb
        else:
            prob +=Xs[i]==Xa[que_restrain_index[index-1]]*va-Xb[i]*vb+Xs[que_restrain_index[index]-1]
        
    prob +=Xa[que_restrain_index[-1]]==0
    suma=sum(Xa)
    sumb=sum(Xb)
    prob +=sum_==suma+sumb
    status = prob.solve()
    return status,prob,Xa,Xb

def get_ret_df(prob,status,Xa,Xb,warehouse_config_time,va,vb,wait_pack,order_sum,p_location):

    time_parts=[(e[1],e[2]) for e in warehouse_config_time]
    a=[e.name for e in Xa]
    b=[e.name for e in Xb]
    name_a_v=[0]*len(a)
    name_b_v=[0]*len(a)
    if status==1:
        for v in prob.variables():
            print(v.name, "=", v.varValue)
            if v.name in a:
                name_a_v[a.index(v.name)]=v.varValue
                continue
            if v.name in b:
                name_b_v[b.index(v.name)]=v.varValue
                continue
            if v.name=='opponit_person':
                opponit_person=v.varValue
            if v.name=='sum_time':
                sum_time=v.varValue
                
        df=pd.DataFrame(data={"工作时间":time_parts,"拣选人数":name_a_v,'打包人数':name_b_v,"总人数":[opponit_person]+['']*(len(time_parts)-1),"总货量":[order_sum]+['']*(len(time_parts)-1),"打包台数量":[p_location]+['']*(len(time_parts)-1),
                              "待打包数量":[wait_pack]+['']*(len(time_parts)-1),"拣选效率":[va]+['']*(len(time_parts)-1),"打包效率":[vb]+['']*(len(time_parts)-1),"总工时":[sum_time]+['']*(len(time_parts)-1)})
        return df,opponit_person,sum_time
    else:
        print(LpStatus[status])
        print("Not Solved---%s,在当前效率下请尝试修改打包台数量或添加人员"%(LpStatus[status]))
        return pd.DataFrame(),None,None
def parse_args():
    
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    parser = argparse.ArgumentParser()
    parser.add_argument('-WAREHOUSE_NAME', help="仓库名称,与配置文件的仓库名称需相一致", required=True,type=str)
    parser.add_argument('-order_sum', help="货物量", required=True, type=int)
    parser.add_argument('-wait_pack', help="待打包量", required=True,default=0, type=int)
    parser.add_argument('-p_location', help="打包台数量", required=True, type=int)
    parser.add_argument('-va', help="拣选效率", required=True, type=float)
    parser.add_argument('-vb', help="打包效率", required=True, type=float)
    parser.add_argument('-current_TIME_QUANTUM', help="所在时间段，比如7:00-8:00，配置中需含有此时间段")
    
    parser.add_argument('-config_filename', help="配置文件路径与名称", required=True)
    parser.add_argument('-ret_save_path', help="结果保存路径名称,需要.xlsx格式", required=True)
    parser.add_argument('-quit', help="y表示终止计算",choices=['y', 'n'],default='n')
    args = vars(parser.parse_args())
    print(args)
    return args

def order_person_main():
    args = parse_args()
    config_filename = args['config_filename']
    WAREHOUSE_NAME = args['WAREHOUSE_NAME']
    order_sum = args['order_sum']
    wait_pack = args['wait_pack']
    p_location = args['p_location']
    
    
    va = args['va']
    vb = args['vb']
    current_TIME_QUANTUM = args['current_TIME_QUANTUM']
    ret_save_path = args['ret_save_path']
    warehouse_config_time=get_config(config_filename,WAREHOUSE_NAME)
    status,prob,Xa,Xb=train_model(warehouse_config_time,current_TIME_QUANTUM,order_sum,wait_pack,p_location,va,vb)
    df,opponit_person,sum_time=get_ret_df(prob,status,Xa,Xb,warehouse_config_time,va,vb,wait_pack,order_sum,p_location)
    if len(df)>0:
        df.to_excel(ret_save_path)

def kill():
    import os,signal
 
    out=os.popen("ps aux | grep pulp/solverdir").read()
    
    for line in out.splitlines():
        try:
            pid = int(line.split()[1])
            os.kill(pid,signal.SIGKILL)
        except Exception as e:
            print(e)
            pass
    



def test():
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', required=True)
    parser.add_argument('-b', required=True)
    args = vars(parser.parse_args())
    a,b=args['a'],args['b']
    print((a,b))

if __name__=="__main__":
    
#    warehouse_config_time=get_config()
#    order_sum =28472
#    p_location =32
#    va =125
#    vb = 165
#    
#    wait_pack=4325
#    current_TIME_QUANTUM='7:00-8:00'
    
#    order_person_main()
#    test()
    order_person_main()
    #配置表.xlsx",WAREHOUSE_NAME='AU Warehouse
    #python real_time_order_person.py -WAREHOUSE_NAME AU_Warehouse -order_sum 28472 -p_location 32 -va 125 -vb 165 -wait_pack 4325 -current_TIME_QUANTUM 7:00-8:00 -config_filename 配置表.xlsx -ret_save_path=ret.xlsx
