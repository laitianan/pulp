# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 14:29:04 2019

@author: tianan.lai
"""

import pandas as pd 
import threading
import datetime
import psutil,os
import json
import os,signal
import logging
import platform   
class RetInfo():
    """
    多线程之间的交流对象，用户存储之间的信息
    """
    def __init__(self):
        ##计算记过存放变量
        self.ret=None
        ##异常信息变量
        self.info=None
        ## 记录pulp是否计算完毕
        self.end=False
        ##开始计算时间记录
        self.currentime=datetime.datetime.now()

    def set_info(self,ret,info,end):
        self.ret=ret
        self.info=info
        self.end=end
    def get_isend(self):
        return self.end

def df2dict(df,status=-1,error_info=''):
    """
    结果DataFrame转换为dict,部分字段去重
    """
    df2dict=dict()
    df2dict['status']=status
    df2dict['info']=error_info
    for column in df.columns:
        if column in ['工作时间','工作时间类型','拣选人数','分拣人数', '打包人数']:
            df2dict[column]=list(df[column].values)
        else:
            col=df[column].unique()
            col=[e for e in col if e!=''][0]
            df2dict[column]=col
#    print(json.dumps(df2dict,ensure_ascii = False))
    return df2dict
        

def parse_args(request,parser):
    """
    请求参数解析
    """
    args=[]
    for e in request.args.items():
        args.append("-{0}={1}".format(e[0],e[1]))
    for e in request.form.items():
        args.append("-{0}={1}".format(e[0],e[1]))
        
    args = vars(parser.parse_args(args))
    
    parameters=[]
    for k,v in args.items():
        parameters.append("%s=%s"%(k,str(v)))
    parameters="&".join(parameters)
    logging.info("请求参数："+parameters)
    return args

def tojson(obj):
    """
    转换为json字符串
    """
    str_ret=json.dumps(obj, ensure_ascii=False)
    logging.info("转换为json字符串结果信息:"+str_ret)
    return str_ret
    
def kill_window():
    """
    window 平台杀死pulp cbc.exe 进程
    """
    try:
        pids = psutil.pids()
        for pid in pids:
            p = psutil.Process(pid)
            # print('pid-%s,pname-%s' % (pid, p.name()))
            if p.name() == 'cbc.exe':
                cmd = 'taskkill /F /IM cbc.exe'
                os.system(cmd)
                logging.info("正常杀死进程cbc.exe")
    except Exception as e :
        logging.error("杀死进程pulp cbc异常"+str(e))
        
        
def kill_linux():
    """
    linux 平台杀死pulp cbc 进程
    """
    out=os.popen("ps aux | grep pulp/solverdir").read()
    lines=out.splitlines()
    if len(lines)>0:
        line=lines[0]
        try:
            pid = int(line.split()[1])
            os.kill(pid,signal.SIGKILL)
            logging.info("正常杀死进程cbc")
        except Exception as e:
            logging.error("杀死进程pulp cbc异常"+str(e))
            print(e)
            
def kill(retInfo,time_lenght=5):
    """
    杀死进程pulp 执行超时，杀死进程
    """
    while not retInfo.end:
        end=datetime.datetime.now()
        gap=end-retInfo.currentime
        if gap.total_seconds()>time_lenght:
            platform_ = platform.system()
            info="执行时间过长已经被kill掉,输入条件造成的计算时间过长，请修改"
            if platform_!='Windows':
                print("kill -s linux--------------------")
                kill_linux()
                print("kill -s linux --------------------")
                retInfo.set_info(None,info,True)
            else:
                kill_window()
                print("kill -s window --------------------")
                retInfo.set_info(None,info,True)
            break
                
def run(retInfo,action,args):
    """
    开启线程执行action方法，其中action在此次指向的是计算排班算法入口函数
    """
    try:
        ret=action(args)
        retInfo.set_info(ret,None,True)
    except Exception as e:
        retInfo.set_info("-1",str(e),True)
        raise e
        
    if not retInfo.end:
        retInfo.set_info(ret,None,True)
        
def sub_process_threading(subaction,args,s=10):
    retInfo=RetInfo()
    #####主计算程序
    t1 = threading.Thread(target=run, args=(retInfo,subaction,args))
    ####主计算程序附加监控进程，强制杀死计算，防止主计算程序pulp计算时间过长
    t2 = threading.Thread(target=kill, args=(retInfo,s))
    t1.start()
    t2.start()
    t2.join()
    ret=retInfo.ret  
    if ret=='-1':
        return {"status":-1,'info':retInfo.info,"data":None}
    
    if ret is not None and ret!='-1':
        return ret
    else:
        return {"status":12,'info':retInfo.info,"data":None}
