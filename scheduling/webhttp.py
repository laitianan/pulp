# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 17:52:31 2019

@author: tianan.lai
"""

from flask import Flask
from flask import request
from flask import jsonify
import  single_order  
import recombination_order
import json
import pandas as pd 
import argparse_adjust
import uuid
import threading
import datetime
import os
import utitly
import logging

logging.basicConfig(level=logging.DEBUG,#控制台打印的日志级别
                    filename='order_system_web.log',
                    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    #a是追加模式，默认如果不写的话，就是追加模式
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] -%(funcName)s: %(message)s'
                    #日志格式
                    )

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return '<h1>Home</h1>'

@app.route('/uploading_config', methods=['POST'])
def uploading_config_api():
    try:
        data = request.form.get('data')
        data = json.loads(data)

        logging.info("uploading_config_api 请求参数：%s"%(str(data)))
        print(data)
        df=dict()
        df["INDEX"]  = data['INDEX']
        df["TIME_QUANTUM"]  = data['TIME_QUANTUM']
        df["WORK_OVERTIME"]  = data['WORK_OVERTIME']
        word_types=[e for e in df["WORK_OVERTIME"] if e not in ['0','-1','1']]
        if len(word_types)>0:
            logging.info("WORK_OVERTIME 字段的取值超过['0','-1','1']")
            raise Exception("WORK_OVERTIME 字段的取值超过['0','-1','1']")
        df["WORK_OVERTIME"]  = data['WORK_OVERTIME']
        df=pd.DataFrame(data)
        WAREHOUSE_NAME= data['WAREHOUSE_NAME']
        df["WAREHOUSE_NAME"] = WAREHOUSE_NAME
        
        columns=['WAREHOUSE_NAME','INDEX','TIME_QUANTUM','WORK_OVERTIME']
        if os.path.exists("./config.xlsx"):
            his_df=pd.read_excel("./config.xlsx")
            his_df=his_df[his_df['WAREHOUSE_NAME']!=WAREHOUSE_NAME]
            df=pd.concat([df[columns],his_df[columns]])
            logging.info("合并历史上班时间表配置信息")
        df=df.to_excel("./config.xlsx",index=False)
    except Exception as e:
        logging.info("uploading_config_api %s"%(str(e)))
        return utitly.tojson({"status":-1,'info':str(e)})
    logging.info("uploading_config_api succeed %s"%(str(WAREHOUSE_NAME)))
    return utitly.tojson({"status":1,'info':'succeed '})

@app.route('/single_order_api', methods=['GET'])
def single_order_api():
    try:
        
    ###http://127.0.0.1:5000/single_order_api?warehouse_name=AU_Warehouse&order_sum=582&wait_pack=4325&opponit_person=100&p_location=57&va=125&vb=165&current_time_quantum=7:00-8:00
    
        parser = argparse_adjust.ArgumentParser(str(uuid.uuid1()))
        parser.add_argument('-warehouse_name', help="仓库名称,与配置文件的仓库名称需相一致", required=True,type=str)
        parser.add_argument('-order_sum', help="货物量", required=True, type=int)
        parser.add_argument('-wait_pack', help="待打包量", required=True,default=0, type=int)
        parser.add_argument('-opponit_person', help="人数", type=int)
        parser.add_argument('-p_location', help="打包台数量", required=True, type=int)
        parser.add_argument('-va', help="拣选效率", required=True, type=float)
        parser.add_argument('-vb', help="打包效率", required=True, type=float)
        parser.add_argument('-current_time_quantum', help="所在时间段，比如7:00-8:00，配置中需含有此时间段,否则将被忽略")
        parser.add_argument('-s', help="超时时间长度,当计算时间超过指定的时间段，则强制杀死进程退出，默认是10秒",default=10, type=int)

        args=utitly.parse_args(request,parser)
        print(args)
#        args={'warehouse_name': 'AU_Warehouse', 'order_sum': 5840072, 'wait_pack': 4325,'opponit_person': 100, 'p_location': 57, 'va': 125.0, 'vb': 165.0, 'current_time_quantum': '19:00-10:00'}
#        ret=single_order.single_order_person_main(args)
        s=args.pop("s")
        ret=utitly.sub_process_threading(single_order.single_order_person_main,args,s)
        status=ret.pop('status')
        info=ret.pop('info')
        if status==10:
            json_ret={"status":status,'info':info,"data":None}
        elif status==12:
            json_ret={"status":status,'info':info,"data":None}
        else:
            json_ret={"status":status,'info':info,"data":ret}

        return utitly.tojson(json_ret)
    except Exception as e:

        return utitly.tojson({"status":-1,'info':str(e),"data":None})
    
    
@app.route('/recombination_order_api', methods=['GET'])
def recombination_order_api():
    """
    http://127.0.0.1:5000/recombination_order_api?warehouse_name=AU_Warehouse&order_sum=44472&wait_sorting=4325&wait_pack=200&p_location=100&va=125.0&vb=265.0&vc=180.0&current_time_quantum=19:00-10:00
    """
    try:
        parser = argparse_adjust.ArgumentParser(str(uuid.uuid1()))
        parser.add_argument('-warehouse_name', help="仓库名称,与配置文件的仓库名称需相一致", required=True,type=str)
        parser.add_argument('-order_sum', help="货物量", required=True, type=int)
        parser.add_argument('-wait_sorting', help="待分拣量", required=True,default=0, type=int)
        parser.add_argument('-wait_pack', help="待打包量", required=True,default=0, type=int)
        parser.add_argument('-opponit_person', help="人数", type=int)
        parser.add_argument('-p_location', help="打包台数量", required=True, type=int)
        parser.add_argument('-va', help="拣选效率", required=True, type=float)
        parser.add_argument('-vb', help="分拣效率", required=True, type=float)
        parser.add_argument('-vc', help="打包效率", required=True, type=float)
        parser.add_argument('-current_time_quantum', help="所在时间段，比如7:00-8:00，配置中需含有此时间段,否则将被忽略")
        parser.add_argument('-s', help="超时时间长度,当计算时间超过指定的时间段，则强制杀死进程退出，默认是10秒",default=10, type=int)
#        args={'warehouse_name': 'AU_Warehouse', 'order_sum': 44472, 'wait_sorting': 4325, 'wait_pack': 200,'opponit_person': None, 'p_location': 100, 'va': 125.0, 'vb': 265.0,'vc': 180.0, 'current_time_quantum': '19:00-10:00', 'config_filename': '配置表.xlsx', 'ret_save_path': 'ret.json'}
        args=utitly.parse_args(request,parser)
#        args={'warehouse_name': 'AU_Warehouse', 'order_sum': 41472, 'wait_sorting': 4325, 'wait_pack': 2000,'opponit_person': None, 'p_location': 100, 'va': 125.0, 'vb': 265.0,'vc': 180.0, 'current_time_quantum': '11:00-12:00'}
#        print(args)
#        args={'warehouse_name': 'AU_Warehouse', 'order_sum': 6641472, 'wait_sorting': 4325, 'wait_pack': 2000, 'opponit_person': None, 'p_location': 100, 'va': 125.0, 'vb': 265.0, 'vc': 180.0, 'current_time_quantum': '11:00-12:00'}
#        import NoSloverException
#        try:
#            ret=recombination_order.recom_order_person_main(args)
##            ret=single_order.single_order_person_main(args)
#        except NoSloverException as e :
#            print(str(e))
        
        s=args.pop("s")
        ret=utitly.sub_process_threading(recombination_order.recom_order_person_main,args,s)
        
        status=ret.pop('status')
        info=ret.pop('info')
        if status==10:
            json_ret={"status":status,'info':info,"data":None}
        elif status==12:
            json_ret={"status":status,'info':info,"data":None}
        else:
            json_ret={"status":status,'info':info,"data":ret}

        return utitly.tojson(json_ret)
    except Exception as e:

        return utitly.tojson({"status":-1,'info':str(e),"data":None})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0')
    ##http://127.0.0.1:5000/uploading_config
