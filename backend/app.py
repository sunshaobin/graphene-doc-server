
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_,not_
from models import *
from manage import *
from flask_cors import CORS
import config
import datetime,time

app = Flask(__name__,
            static_folder = "../frontend/dist/static",
            template_folder = "../frontend/dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config.from_object(config)
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'
db = SQLAlchemy(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    return render_template("index.html")

#登录
@app.route('/api/login/', methods=['POST'])
def login():
    msg=''
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            session['username'] = request.form.get('username')
            msg='success'
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

#获取当前登录用户
@app.route('/api/get_user/',methods=['GET'])
def get_user():
    if session['username']==None: 
        response={
            'username':'',
            'password':'',
            'email':''
        }
    else:
        user = get_user_byusername(session['username'])
        response={
            'username':user.username,
            'password':user.password,
            'email':user.email
        }
    return jsonify(response)

@app.route('/api/logout/',methods=['GET'])
def logout():
    msg='退出成功'
    session['username']=None
    response={
        'message':msg
    }
    return jsonify(response)

#注册
@app.route('/api/regist/', methods=['POST'])
def regist():
    msg=''
    if request.method == 'POST':
        username = User.query.filter(User.username == request.form['username']).first()
        email = User.query.filter(User.email == request.form['email']).first()
        if(username or email):
            msg='用户名或邮箱不能重复！'
        else:
            msg="成功注册！"
            id=get_newid()
            newUser=User(id=id, username=request.form['username'], password=request.form['password'], email=request.form['email'])
            db.session.add(newUser)
            db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

@app.route('/api/getalluser/',methods=['GET'])
def getalluser():
    all_user=User.query.all()
    res=[]
    context={}
    for user in all_user:
        context={
            'username':user.username,
            'password':user.password,
            'email':user.email
        }
        res.append(context)
    return jsonify(res)

# 修改密码
@app.route('/api/modifypwd/', methods=['POST'])
def modifypwd():
    msg = None
    if request.method == 'POST':
        user = User.query.filter(User.username==session['username']).first()
        session['password'] = user.password
        if (session['password']!=request.form['oldpassword']):
            msg = '原密码错误！'
        elif(request.form['newpassword1']!=request.form['newpassword2']):
            msg = '两次密码不一致！'
        else:
            session['password']=request.form['newpassword1']
            get_user_byusername(session['username']).update({"password":request.form['newpassword1']})
            db.session.commit()
            msg = 'success'

    response={
        'message':msg
    }
    return jsonify(response)

@app.route('/api/creategroup/',methods=['POST'])
def creategroup():
   user=get_user_byusername(session['username'])
   id=get_newid()
   newGroup=Group(id=id,groupname=request.form['groupname'],leaderid=user.id,createdtime=datetime.datetime.now(),description=request.form['description'])
   db.session.add(newGroup)
   db.session.commit()
   response={
       'message':'创建团队成功！'
   }
   return jsonify(response)

@app.route('/api/mygroup/',methods=['GET'])
def mygroup():
    user=get_user_byusername(session['username'])
    all_group=Group.query.filter(Group.leaderid==user.id)
    res=[]
    context={}
    for group in all_group:
        context={
            'groupid':group.id,
            'groupname':group.groupname,
            'description':group.description,
            'createdtime':group.createdtime
        }
        res.append(context)
    return jsonify(res)

@app.route('/api/addgroupmember/',methods=['POST'])
def addgroupmember():
    userid=request.form['userid']
    groupid=request.form['groupid']
    id=get_newid()
    newGroupMember=GroupMember(id=id,user_id=userid,group_id=groupid)
    db.session.add(newGroupMember)
    db.session.commit()
    response={
        'message':'添加成员成功！'
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug = True)
