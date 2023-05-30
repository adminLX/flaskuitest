# -*- encoding: utf-8 -*-
"""
@File:casecommon.py
@Author：lixu
2023/5/13 17:46
"""
import json
import subprocess
from http import server
import datetime

from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
import os
import ftputil
class UTF8FTPHost(ftputil.FTPHost):
    def _make_session(self, *args, **kwargs):
        session = super()._make_session(*args, **kwargs)
        # 设置UTF-8编码
        session.encoding = "utf-8"
        return session

from app import app
# app = Flask(__name__,static_url_path='/uploads')
# 数据库配置
db_config = {
    'host': '192.168.32.88',
    'user': 'root',
    'password': '123456',
    'database': 'test01',
    'charset':'utf8'
}

# FTP配置
ftp_config = {
    'host': '10.8.1.201',
    'port': 21,
    'user': 'noxuser',
    'password': 'duodian@123456'

}

# app = Flask(__name__, static_url_path='/static')

# 连接数据库
mydb = mysql.connector.connect(**db_config)
mycursor = mydb.cursor()
@app.route('/save-image-data', methods=['POST'])
def save_image_data():
    print("save_image_data called")  # 添加此行，可以确保函数被调用
    print(request.json)  #打印接收到的 JSON 数据
    data = request.get_json()
    print(123)
    print(data)
    if data:
        department_id = data['department_id']
        project_id = data['project_id']
        image_name = data['image_name']
        action_type = data['action_type']
        step_number = data['step_number']
        script_name = data['script_name']
        ftp_path = data['ftp_path']  # 获取新字段
        image_data = (script_name, image_name, action_type, step_number, department_id, project_id, ftp_path)
        print(image_data)
        save_image_information_to_database(image_data)
        return jsonify(result='success'), 200

    else:
        return jsonify(result='error'), 400
@app.route('/upload-image', methods=['POST'])
def upload_image():
    if request.files:
        image_file = request.files['image']
        script_name = request.form['script_name']+'.air'
        department_id = int(request.form['department_id']) # 新增加这行
        project_id = int(request.form['project_id'])       # 新增加这行
        # 获取部门和项目名称
        mycursor.execute("SELECT name FROM department WHERE id = %s", (department_id, ))
        department_name = mycursor.fetchone()[0]
        mycursor.execute("SELECT name FROM project WHERE id = %s", (project_id, ))
        project_name = mycursor.fetchone()[0]
        # 创建文件夹
        # script_folder = os.path.join(os.getcwd(), 'uploads', script_name)
        new_path = os.path.join(os.getcwd(), 'uploads', department_name, project_name, script_name)
        local_img_path = os.path.join('uploads', department_name, project_name, script_name, image_file.filename)

        if not os.path.exists(new_path):
            os.makedirs(new_path)
        image_file.save(local_img_path)

        #使用FTP上传图片文件
        with UTF8FTPHost(ftp_config['host'], ftp_config['user'], ftp_config['password']) as ftp_host:
            # 检查目录是否存在，如果不存在则创建目录
            # remote_dir = f'/bignoxData/bignoxData/software/qa/Mobile/uitest/{script_name}'
            remote_dir = f'/bignoxData/bignoxData/software/qa/Mobile/uitest/{department_name}/{project_name}/{script_name}' # 修改 remote_dir 为新的路径结构
            if not ftp_host.path.exists(remote_dir):
                ftp_host.makedirs(remote_dir)
            ftp_path = f'{remote_dir}/{image_file.filename}'
            ftp_host.upload(local_img_path, ftp_path)
        return jsonify({'image_url': f'/uploads/{department_name}/{project_name}/{script_name}/{image_file.filename}'})
    else:
        return jsonify({'error': 'No image file uploaded.'}), 400

def save_image_information_to_database(image_data):
    query = ("INSERT INTO script_images(script_name, image_name, action_type, step_number, department_id, project_id, ftp_path) VALUES (%s, %s, %s, %s, %s, %s, %s)")
    mycursor.execute(query, image_data)
    mydb.commit()



@app.route('/generate-test-script', methods=['POST'])
def generate_test_script():
    try:
        print("开始处理请求")
        print(request.headers)  # 打印请求头，了解 Content-Type 是否正确
        print(request.json)  # 打印接收到的 JSON 数据
        if request.json:
            script_name = request.json.get('script_name')
            script_nameair = request.json.get('script_name')+'.air'
            department_id = int(request.json.get('department_id'))
            project_id = int(request.json.get('project_id'))
            # 在调用 int() 函数之前，请检查部门ID和项目ID的值
            print(f"部门ID: {request.json.get('department_id')}")
            print(f"项目ID: {request.json.get('project_id')}")
            if department_id is None or project_id is None:
                # 如果 department_id 或 project_id 为 None，返回错误消息
                return jsonify({'error': '部门ID或项目ID不能为空.'}), 400
                department_id = int(department_id)
                project_id = int(project_id)
            # 查询数据库中有关该脚本的所有图片信息
            mycursor.execute("SELECT image_name, action_type, step_number, ftp_path FROM script_images WHERE script_name = %s ORDER BY step_number", (script_name, ))
            images_data = mycursor.fetchall()
            # 获取部门和项目名称
            mycursor.execute("SELECT name FROM department WHERE id = %s", (department_id, ))
            department_name = mycursor.fetchone()[0]
            mycursor.execute("SELECT name FROM project WHERE id = %s", (project_id, ))
            project_name = mycursor.fetchone()[0]
            # 更新 script_folder 路径为新的路径结构
            script_folder = os.path.join(os.getcwd(), 'uploads', department_name, project_name, script_nameair)
            if not os.path.exists(script_folder):
                os.makedirs(script_folder)
            # 生成Airtest测试脚本
            with open(os.path.join(script_folder, f"{script_name}.py"), "w") as f:
                f.write("from airtest.core.api import *\n")
                f.write("auto_setup(__file__)\n")
                for image_data in images_data:
                    image_name, action_type, step_number, _ = image_data
                    if action_type == 'click':
                        f.write(f"touch(Template(r'{image_name}'))\n")
                    elif action_type == 'assert':
                        f.write(f"assert_exists(Template(r'{image_name}'))\n")

                # f.write("device().stop_app()")
                        # 根据 department_id 和 project_id 生成本地新生成的 .air 的文件路径
            script_path = f"local/scripts/{department_id}/{project_id}/{script_name}.air"
            # 获取当前时间
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 将脚本信息插入到新创建的 scripts 表中
            mycursor.execute("""
            INSERT INTO scripts (
                department_id, project_id, script_name, create_time, script_path, run_result
            ) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
                             (department_id, project_id, script_name, now, script_path, '未运行'))
            mydb.commit()
            script_id = mycursor.lastrowid
            return jsonify({'result': 'success','id':script_id})
        else:
            return jsonify({'error': 'No script name found.'}), 400
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/uploads/<department_name>/<project_name>/<script_name>/<filename>')
def send_static_file(department_name, project_name, script_name, filename):     # 更正参数
    updated_upload_path = os.path.join(os.path.dirname(app.root_path), 'uploads', department_name, project_name, script_name)     # 更新路径
    return send_from_directory(updated_upload_path, filename)

#添加一个新的路由和函数，用于获取部门数据
@app.route('/get-departments', methods=['GET'])
def get_departments():
    mycursor.execute("SELECT id, name FROM department")
    departments = mycursor.fetchall()
    #print(departments)
    departments_list = [{'id': d[0], 'name': d[1]} for d in departments]
    return jsonify({'departments': departments_list})

#部门项目创建---------------------------------------------------------
@app.route('/get-department-list', methods=['GET'])
def get_department_list():
    mycursor.execute("SELECT id, name FROM department")
    departments = mycursor.fetchall()
    departments_list = [{'id': d[0], 'name': d[1]} for d in departments]
    return jsonify({'departments': departments_list})
@app.route('/create-project', methods=['POST'])
def create_project():
    project_name = request.json.get('name')
    department_id = request.json.get('department_id')
    mycursor.execute("INSERT INTO project (name, department_id) VALUES (%s, %s)", (project_name, department_id))
    mydb.commit()
    return jsonify({'result': '项目已创建'}), 200

@app.route('/get-projects', methods=['GET'])
def get_projects():
    department_id = request.args.get('department_id')

    mycursor.execute("SELECT id, department_id, name FROM project WHERE department_id = %s", (department_id,))
    projects = mycursor.fetchall()

    data = []
    for project in projects:
        data.append({
            'id': project[0],
            'department_id': project[1],
            'name': project[2]
        })

    return jsonify({'projects': data}), 200

@app.route('/delete-project', methods=['POST'])
def delete_project():
    project_id = request.json.get('id')
    mycursor.execute("DELETE FROM project WHERE id = %s", (project_id,))
    mydb.commit()
    return jsonify({'result': '项目已删除'}), 200
#~~~~~~~~~~~~~~~项目管理路由函数~~~~~~~~~~~
@app.route('/get-all-departments', methods=['GET'])
def get_all_departments():
    mycursor.execute("SELECT id, name FROM department")
    departments = mycursor.fetchall()
    departments_list = [{'id': d[0], 'name': d[1]} for d in departments]
    return jsonify({'departments': departments_list})
@app.route('/get-projects-by-depid', methods=['POST'])
def get_projects_by_depid():
    if request.json:
        dep_id = request.json.get('department_id')
        mycursor.execute("SELECT p.id, d.name as department_name, p.name as project_name FROM project p INNER JOIN department d ON p.department_id = d.id WHERE p.department_id = %s", (dep_id, ))
        projects = mycursor.fetchall()
        projects_list = [{'id': p[0], 'department_name': p[1], 'project_name': p[2]} for p in projects]
        return jsonify({'projects': projects_list})
    else:
        return jsonify({'error': 'No department id found.'}), 400
@app.route('/get-projects-by-depid', methods=['POST'])
def get_projects_by_depidtwo():
    print(request.json)
    if request.json:
        department_id = request.json.get('department_id')
        mycursor.execute("SELECT p.id, d.name as department_name, p.name as project_name FROM project p INNER JOIN department d ON p.department_id = d.id WHERE p.department_id = %s",
                         (department_id,))
        projects = mycursor.fetchall()
        projects_list = [{'id': p[0], 'department_name': p[1], 'project_name': p[2]} for p in projects]
        return jsonify({'projects': projects_list})
    else:
        return jsonify({'error': 'No department id found.'}), 400
@app.route('/add-project', methods=['POST'])
def add_project():
    if request.json:
        dep_id = request.json.get('department_id')
        project_name = request.json.get('project_name')
        query = ("INSERT INTO project(department_id, name) VALUES (%s, %s)")
        mycursor.execute(query, (dep_id, project_name,))
        mydb.commit()
        return jsonify({'result': 'success'})
    else:
        return jsonify({'error': 'No department id or project name found.'}), 400

@app.route('/delete-project-by-id', methods=['POST'])
def delete_project_by_id():
    if request.json:
        project_id = request.json.get('project_id')
        mycursor.execute("DELETE FROM project WHERE id=%s", (project_id,))
        mydb.commit()
        return jsonify({'result': 'success'})
    else:
        return jsonify({'error': 'No project id found.'}), 400

# 获取项目名称的函数
def get_project_name(project_id):
    mycursor.execute("SELECT name FROM project WHERE id = %s", (project_id,))
    project_name = mycursor.fetchone()[0]
    return project_name
#获取下拉框内所有的项目名
@app.route('/get-projects-select', methods=['GET'])
def get_projects_select():
    department_id = request.args.get('department_id')
    if department_id:
        mycursor.execute("SELECT id, department_id, name FROM project WHERE department_id = %s", (department_id,))
        projects = mycursor.fetchall()
        data = []
        for project in projects:
            data.append({
                'id': project[0],
                'department_id': project[1],
                'name': project[2]
            })
        return jsonify({'projects': data}), 200
    else:
        return jsonify({'error': '请提供部门 ID'}), 400
#-----------------
@app.route('/delete-script/<int:script_id>', methods=['POST'])
def delete_script(script_id):
    # 删除数据库记录
    mycursor.execute('DELETE FROM scripts WHERE id=%s', (script_id,))
    mydb.commit()

    return jsonify({"result": "success"})
@app.route('/run-script/<int:script_id>', methods=['POST'])
def run_script(script_id):
    mycursor.execute("SELECT script_path FROM scripts WHERE id=%s", (script_id,))
    script_path = mycursor.fetchone()[0]

    cmd = f'D:\\myairtest\\AirtestIDE-win-1.2.13\\AirtestIDE\\AirtestIDE runner "{script_path}" --device android://127.0.0.1:5037/127.0.0.1:62001?cap_method=JAVACAP&touch_method=MINITOUCH& --log "C:\\Users\\Nox258\\AppData\\Local\\Temp\\AirtestIDE\\scripts\\3c5a0fe5f2e1ece4dd7e21b0f74f70f7"'

    # 在后端运行cmd命令
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return jsonify({"result": "success"})