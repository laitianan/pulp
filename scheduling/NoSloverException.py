# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 15:22:56 2019

@author: tianan.lai
"""

class NoSloverException(Exception):
    '''自定义异常类'''
    def __init__(self, message, status=None):
        super().__init__(message, status)
        self.message = message
    def __str__(self):
        return "运筹学无解："+self.message

    
    

