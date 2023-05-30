# -*- encoding: utf-8 -*-
"""
@File:__init__.py.py    
@Author：lixu      
2023/5/11 15:08
"""
#此文件为将所有的
from flask import Flask
# app = Flask(__name__)
app = Flask(__name__, static_url_path='/uploads', static_folder='uploads')
# 导入其他包含路由和逻辑处理程序的模块
from app import index,casecommon