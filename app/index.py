# -*- encoding: utf-8 -*-
"""
@File:index.py    
@Author：lixu      
2023/5/11 19:50
"""
from flask import render_template
from app import app
import json
from flask import request, jsonify
from app import app
@app.route('/')
def test01():
    return render_template('homepage.html')
@app.route('/togeneratecase')
def load_indexthree():
    return render_template('togeneratecase.html')
#index此文件均是加载的所有路由路径
@app.route('/departments')
def departments():
    return render_template('departments.html')
@app.route('/project_management')
def project_management():
    return render_template('project_management.html')
@app.route('/projects')
def projects():
    return render_template('projects.html')
