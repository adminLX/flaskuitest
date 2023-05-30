# -*- encoding: utf-8 -*-
"""
@File:common_dep.py
@Author：lixu
2023/4/22 13:48
"""
from http import server
from flask import Flask, request, jsonify
import mysql.connector
from app import app
import mysql.connector
# 连接MySQL数据库
mydb = mysql.connector.connect(
    host="192.168.32.88",
    user="root",
    password="123456",
    charset='utf8mb4'
)

# 创建数据库和数据表
mycursor = mydb.cursor()
# mycursor.execute("CREATE DATABASE IF NOT EXISTS mydatabase")
mycursor.execute("USE mydatabase")
# mycursor.execute("CREATE TABLE IF NOT EXISTS mytable (id INT AUTO_INCREMENT PRIMARY KEY, department_id INT NOT NULL, project_name VARCHAR(255) NOT NULL, belong_to VARCHAR(255) NOT NULL, update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)")
mycursor.close()
# 增加数据接口
@app.route('/add', methods=['POST'])
def add_data():
    try:
        data = request.get_json()
        department_id = data['department_id']
        project_name = data['project_name']
        belong_to = data['belong_to']

        # 插入数据到数据表中
        mycursor = mydb.cursor()
        sql = "INSERT INTO mytable (department_id, project_name, belong_to) VALUES (%s, %s, %s)"
        val = (department_id, project_name, belong_to)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
        return jsonify({'message': 'Data added successfully!'})
    except Exception as e:
        # 发生异常时回滚并返回错误信息
        mydb.rollback()
        return jsonify({'error_message': str(e)})
# 查询数据接口
@app.route('/get', methods=['GET'])
def get_data():
    try:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM mytable")
        result = mycursor.fetchall()
        mycursor.close()

        data = []
        for row in result:
            item = {
                'id': row[0],
                'department_id': row[1],
                'project_name': row[2],
                'belong_to': row[3],
                'update_time': row[4].strftime('%Y-%m-%d %H:%M:%S')
            }
            data.append(item)
        print(data)
        return jsonify({'data': data})
    except Exception as e:
        # 发生异常时回滚并返回错误信息
        mydb.rollback()
        return jsonify({'error_message': str(e)})
# 修改数据接口
@app.route('/update/<int:id>', methods=['PUT'])
def update_data(id):
    try:
        data = request.get_json()
        department_id = data['department_id']
        project_name = data['project_name']
        belong_to = data['belong_to']

        # 更新数据表中的数据
        mycursor = mydb.cursor()
        sql = "UPDATE mytable SET department_id = %s, project_name = %s, belong_to = %s WHERE id = %s"
        val = (department_id, project_name, belong_to, id)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()

        return jsonify({'message': 'Data updated successfully!'})
    except Exception as e:
        # 发生异常时回滚并返回错误信息
        mydb.rollback()
        return jsonify({'error_message': str(e)})
# 删除数据接口
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_data(id):
    try:
        # 删除数据表中指定的数据
        mycursor = mydb.cursor()
        sql = "DELETE FROM mytable WHERE id = %s"
        val = (id,)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()

        return jsonify({'message': 'Data deleted successfully!'})
    except Exception as e:
        # 发生异常时回滚并返回错误信息
        mydb.rollback()
        return jsonify({'error_message': str(e)})
