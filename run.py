# -*- encoding: utf-8 -*-
"""
@File:run.py    
@Author：lixu      
2023/5/11 15:11
"""
from http import server
from urllib import request
from app import app
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True,port=9555)
    server.logger.info('info log')
    server.logger.info('【请求方法】{}【请求路径】{}【请求地址】{}'.format(request.method, request.path, request.remote_addr))