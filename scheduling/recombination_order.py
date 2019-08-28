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
import logging
import NoSloverException
from  utitly  import df2dict
#assert order_sum+wait_pack>=va*2,"数据量太小,本程序不支持,请人工处理"

def train_model(warehouse_config_time,current_time_quantum,order_sum,wait_sorting,wait_pack,p_location,va,vb,vc,opponit_person=None):
    
    if p_location<0 or order_sum<0 or wait_sorting<0 or wait_pack<0 or va<0 or vb<0 or vc<0:
        logging.error("存在参数小于0")
        raise Exception("存在参数小于0")
    if opponit_person!=None and opponit_person<0:
        logging.error("存在参数小于0")
        raise Exception("存在参数小于0")
    
    upBound_person=100
    index=-1
    for i,TIME_QUANTUM,label in warehouse_config_time:
        if TIME_QUANTUM==current_time_quantum:
            index=i
            break
        
    warehouse_config_time=[e if e[0]>=index else (e[0],e[1],-1) for e in warehouse_config_time]
    
    Xa=[LpVariable("a%s"%(e[0]), lowBound=0,upBound=upBound_person,cat=pulp.LpInteger) for e in warehouse_config_time]
    
    Xb=[LpVariable("b%s"%(e[0]), lowBound=0,upBound=upBound_person,cat=pulp.LpInteger) for e in warehouse_config_time]
    
    Xc=[LpVariable("c%s"%(e[0]), lowBound=0,upBound=upBound_person,cat=pulp.LpInteger) for e in warehouse_config_time]
    
    
    sum_=LpVariable("sum_time", lowBound=0 ,cat=pulp.LpInteger)
    if opponit_person!=None:
        ####排班优化最小工时
        z=0
        z+=sum([e*i for i,e in enumerate(Xa, start=2)])
        z+=sum([e*i for i,e in enumerate(Xb, start=1)])
        z+=sum([e*i for i,e in enumerate(Xc, start=1)])
        prob = LpProblem('orderperson', LpMinimize)
        prob += z
        ###人工安排，计算状态为0的正常上班区间和加班时间段状态为1
        que_restrain_index=[e[0] for e in warehouse_config_time if e[2]!=-1]
        que_finish_index=[e[0] for e in warehouse_config_time if e[2]==-1]
        print(z)
    else:
        ####计算需要出勤人数优化最小出勤人数
        opponit_person= LpVariable("opponit_person", lowBound=0,upBound=upBound_person,cat=pulp.LpInteger)
        z =opponit_person
        prob = LpProblem('opponit-person', LpMinimize)
        prob += z
        ###计算需要多少人数，只需要计算状态为0的正常上班区间
        que_restrain_index=[e[0] for e in warehouse_config_time if e[2]==0]
        que_finish_index=[e[0] for e in warehouse_config_time if e[2]!=0]
    sum_a=0
    for e in Xa:
        sum_a+=e*va
    sum_b=0
    for e in Xb:
        sum_b+=e*vb
    sum_c=0
    for e in Xc:
        sum_c+=e*vc
        
    prob +=sum_a>=order_sum
    prob +=sum_b>=order_sum+wait_sorting
    prob +=sum_c>=order_sum+wait_pack+wait_sorting
    #####Xsa  各个时间段剩下的待分拣量
    Xsa=[]
    #####Xsb  各个时间段剩下的待打包量
    Xsb=[]
    for e in que_finish_index:
        Xsa.append((e,LpVariable("sa%s"%(e), lowBound=0)))
        Xsb.append((e,LpVariable("sb%s"%(e), lowBound=0)))
        
    throld_low=-1*max([va,vb,vc])
    for index,e in enumerate(que_restrain_index):
        if index==len(que_restrain_index)-1:
            Xsa.append((e,LpVariable("sa%s"%(e), lowBound=throld_low, upBound=vb)))
            Xsb.append((e,LpVariable("sb%s"%(e), lowBound=throld_low, upBound=vb)))
        else:
            Xsa.append((e,LpVariable("sa%s"%(e), lowBound=throld_low)))
            Xsb.append((e,LpVariable("sb%s"%(e), lowBound=throld_low)))
            
    ###########
    Xsa=[e[1] for e in sorted(Xsa,key=lambda x:x[0])]
    Xsb=[e[1] for e in sorted(Xsb,key=lambda x:x[0])]
    
    for i in que_finish_index:
        prob +=Xa[i]==0
        prob +=Xb[i]==0
        prob +=Xc[i]==0
        prob +=Xsa[i]==0
        prob +=Xsb[i]==0
        
    for index,i in enumerate(que_restrain_index):
        prob +=Xa[i]+Xb[i]+Xc[i]<=opponit_person
        prob +=Xc[i]<=p_location
#       
        if index<len(que_restrain_index)-1:
            ###拣选人数
            prob +=Xa[que_restrain_index[index]]>=Xa[que_restrain_index[index+1]]
            
            prob +=Xa[que_restrain_index[index]]+Xb[que_restrain_index[index]]+Xc[que_restrain_index[index]]>=Xa[que_restrain_index[index+1]]+Xb[que_restrain_index[index+1]]+Xb[que_restrain_index[index+1]]
            
        if index==0:
            prob +=Xsa[i]==wait_sorting-Xb[i]*vb
            prob +=Xsb[i]==wait_pack+Xb[i]*vb-Xc[i]*vc
        else:
#            prob +=Xb[i]<=Xc[i]*1.3
            prob +=Xsa[i]==Xa[que_restrain_index[index-1]]*va-Xb[i]*vb+Xsa[que_restrain_index[index]-1]
            
            prob +=Xsb[i]==Xb[i]*vb+Xsb[que_restrain_index[index]-1]-Xc[i]*vc
            
            if index<len(que_restrain_index)-1:
                prob +=Xb[que_restrain_index[index]]>=Xb[que_restrain_index[index+1]]
#                prob +=Xc[que_restrain_index[index]]<=Xc[que_restrain_index[index+1]]
    
    prob +=Xa[que_restrain_index[-1]]==0
    suma=sum(Xa)
    sumb=sum(Xb)
    sumc=sum(Xc)
    prob +=sum_==suma+sumb+sumc
    status = prob.solve()
    return status,prob,Xa,Xb,Xc

def get_ret_df(prob,status,Xa,Xb,Xc,warehouse_config_time,va,vb,vc,wait_sorting,wait_pack,order_sum,p_location,opponit_person=None):
    """
    运筹学计算引擎结果抽象成DataFrame
    """
    time_parts=[e[1] for e in warehouse_config_time]
    time_type=[str(e[2]) for e in warehouse_config_time]
    a=[e.name for e in Xa]
    b=[e.name for e in Xb]
    c=[e.name for e in Xc]
    name_a_v=[0]*len(a)
    name_b_v=[0]*len(a)
    name_c_v=[0]*len(c)
    if status==1:
        for v in prob.variables():
            print(v.name, "=", v.varValue)
            if v.name in a:
                name_a_v[a.index(v.name)]=v.varValue
                continue
            if v.name in b:
                name_b_v[b.index(v.name)]=v.varValue
                continue
            if v.name in c:
                name_c_v[c.index(v.name)]=v.varValue
                continue
            if v.name=='sum_time':
                sum_time=v.varValue
            if opponit_person==None:
                if v.name=='opponit_person':
                    opponit_person=v.varValue
            else:
                pass
                
        df=pd.DataFrame(data={"工作时间":time_parts,"工作时间类型":time_type,"拣选人数":name_a_v,"分拣人数":name_b_v,'打包人数':name_c_v,"总人数":[opponit_person]+['']*(len(time_parts)-1),"总货量":[order_sum]+['']*(len(time_parts)-1),"打包台数量":[p_location]+['']*(len(time_parts)-1),
                              "待分拣数量":[wait_sorting]+['']*(len(time_parts)-1),"待打包数量":[wait_pack]+['']*(len(time_parts)-1),"拣选效率":[va]+['']*(len(time_parts)-1),"分拣效率":[vb]+['']*(len(time_parts)-1),"打包效率":[vc]+['']*(len(time_parts)-1),"总工时":[sum_time]+['']*(len(time_parts)-1)})
        return df,sum_time,status,""
    else:
        print(LpStatus[status])
        print("Not Solved---%s,在当前效率下请尝试修改打包台数量|添加人员|可工作时间过短"%(LpStatus[status]))
        df=pd.DataFrame()
        return df,None,status,"Not Solved---%s,在当前效率下请尝试修改打包台数量|添加人员|可工作时间过短"%(LpStatus[status])
    
def parse_args():
    
#    if len(sys.argv) == 1:
#        sys.argv.append('-h')
#
   # parser = argparse.ArgumentParser()
#    parser.add_argument('-warehouse_name', help="仓库名称,与配置文件的仓库名称需相一致", required=True,type=str)
#    parser.add_argument('-order_sum', help="货物量", required=True, type=int)
#    parser.add_argument('-wait_sorting', help="待分拣量", required=True,default=0, type=int)
#    parser.add_argument('-wait_pack', help="待打包量", required=True,default=0, type=int)
#    parser.add_argument('-opponit_person', help="人数", type=int)
#    parser.add_argument('-p_location', help="打包台数量", required=True, type=int)
#    parser.add_argument('-va', help="拣选效率", required=True, type=float)
#    parser.add_argument('-vb', help="分拣效率", required=True, type=float)
#    parser.add_argument('-vc', help="打包效率", required=True, type=float)
#    parser.add_argument('-current_time_quantum', help="所在时间段，比如7:00-8:00，配置中需含有此时间段,否则将被忽略")
#    
#    parser.add_argument('-config_filename', help="配置文件路径与名称", required=True)
#    parser.add_argument('-ret_save_path', help="结果保存路径名称,需要.xlsx格式", required=True)
#    args = vars(parser.parse_args())
#    print(args)
    
    args={'warehouse_name': 'AU_Warehouse', 'order_sum': 44472, 'wait_sorting': 4325, 'wait_pack': 200,'opponit_person': None, 'p_location': 100, 'va': 125.0, 'vb': 265.0,'vc': 180.0, 'current_time_quantum': '19:00-10:00', 'config_filename': '配置表.xlsx', 'ret_save_path': 'ret.json'}
    
    return args

def recom_order_person_main(args):
#    import time
#    time.sleep(7)
    warehouse_name = args['warehouse_name']
    order_sum = args['order_sum']
    wait_sorting = args['wait_sorting']
    wait_pack = args['wait_pack']
    opponit_person=args['opponit_person']
    p_location = args['p_location']
    va = args['va']
    vb = args['vb']
    vc = args['vc']
    current_time_quantum = args['current_time_quantum']
    
    warehouse_config_time=get_config(warehouse_name=warehouse_name)
    
    if opponit_person is None:
        status,prob,Xa,Xb,Xc=train_model(warehouse_config_time,current_time_quantum,order_sum,wait_sorting,wait_pack,p_location,va,vb,vc)
        if status==-1:
#            raise NoSloverException("Not Solved---%s,在当前效率下请尝试修改打包台数量|添加人员|可工作时间过短"%(LpStatus[status]))
            info="Not Solved---%s,在当前效率下请尝试修改打包台数量|添加人员|可工作时间过短"%(LpStatus[status])
            return df2dict(pd.DataFrame(),10,info)
        else:
            opponit_person=value(prob.objective)
            logging.info("opponit_person总人数:%s"%opponit_person)
            for v in prob.variables():
                print(v.name, "=", v.varValue)
            print("总人数%s"%opponit_person)
            
    status,prob,Xa,Xb,Xc=train_model(warehouse_config_time,current_time_quantum,order_sum,wait_sorting,wait_pack,p_location,va,vb,vc,opponit_person)
    for v in prob.variables():
        print(v.name, "=", v.varValue)
    print("总人数%s"%opponit_person)
    print(value(prob.objective),'最小值')
    df,sum_time,status,info=get_ret_df(prob,status,Xa,Xb,Xc,warehouse_config_time,va,vb,vc,wait_sorting,wait_pack,order_sum,p_location,opponit_person)

    if len(df)>0:
        logging.info("stauts:11 :info:succeed")
        return df2dict(df,11,"succeed ")
    else:
        logging.info("stauts:10 :info:%s"%(str(info)))
        return df2dict(df,10,info)
    
    


if __name__=="__main__":
    
    args = parse_args()
    df=recom_order_person_main(args)
    #配置表.xlsx",warehouse_name='AU Warehouse
    #python recombination_order.py -warehouse_name AU_Warehouse -order_sum 28472 -p_location 32 -va 125 -vb 165 -vc 180 -wait_pack 4325 -wait_sorting 0 -opponit_person 57 -current_time_quantum 7:00-8:00 -config_filename 配置表.xlsx -ret_save_path=ret.json
