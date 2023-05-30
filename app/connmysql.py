# -*- encoding: utf-8 -*-
"""
@File:connmysql.py    
@Author：lixu      
2023/5/11 20:13
"""
import mysql.connector
# 连接MySQL数据库
mydb = mysql.connector.connect(
    host="192.168.32.88",
    user="root",
    password="123456",
    charset='utf8'
)

# 创建数据库和数据表
mycursor = mydb.cursor()
# mycursor.execute("CREATE DATABASE IF NOT EXISTS mydatabase")
mycursor.execute("USE mydatabase")
# mycursor.execute("CREATE TABLE IF NOT EXISTS mytable (id INT AUTO_INCREMENT PRIMARY KEY, department_id INT NOT NULL, project_name VARCHAR(255) NOT NULL, belong_to VARCHAR(255) NOT NULL, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)")
mycursor.close()