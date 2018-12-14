#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import time
import sys
from io import BytesIO
#import importlib #for Python 3x

from flask import Flask, jsonify, request, send_from_directory, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TEXT, DATETIME, and_, BOOLEAN
from sqlalchemy.dialects.mysql import LONGTEXT

import hashlib

from config import USER, PASSWORD, URL, PORT, DATABASE
from ext import redis0, redis2

##import pymysql# for Python 3x
##pymysql.install_as_MySQLdb()# for Python 3x

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
##    importlib.reload(sys) #for Python 3x
    reload(sys)
    sys.setdefaultencoding(default_encoding)

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(USER, PASSWORD, URL, PORT, DATABASE) # for Python 3x
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}:{}/{}'.format(USER, PASSWORD, URL, PORT, DATABASE)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)

class Like(db.Model):

    __tablename__ = 'like'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32))
    videoid = db.Column(db.Integer)

    def __init__(self, name, videoid):
        self.username = name
        self.videoid = videoid


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(32))
    username = db.Column(db.String(32), unique=True, index=True)
    password = db.Column(db.String(128))
    # token = db.Column(db.String(128), index=True)
    bitmap = db.Column(LONGTEXT)

    def __init__(self, nickname, name, pwd):
        self.nickname = nickname
        self.username = name
        self.password = pwd
        self.id = None
        self.bitmap = None


class Video(db.Model):

    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32))
    video = db.Column(db.String(256), unique=True, index=True)
    title = db.Column(TEXT)
    topic = db.Column(db.String(128))
    location = db.Column(TEXT)
    deleted = db.Column(BOOLEAN)
    time = db.Column(DATETIME)

    def __init__(self, username, video_, title, topic, location, deleted, time_):
        self.username = username
        self.video = video_
        self.title = title
        self.topic = topic
        self.location = location
        self.deleted = deleted
        self.time = time_


# @auth.verify_token
# def verify_token(token):
#     g.user = None
#     if redis0.exists(token):
#         g.user = redis0.get(token)
#         return True
#     return False




@app.route('/login', methods=['POST'])
def login():
    # g.user = None
    username = request.form['username']
    password = hashlib.md5(request.form['password']).hexdigest()
    token = hashlib.md5(request.form['token']).hexdigest()
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({
            'success': False,
            'content': 'Unknown Username!',
            'bitmap': None
        })
    else:
        if user.password == password:
            # redis.delete(user.token)
            # redis.expire(user.token, 2592000)
            redis0.set(token, user.username)
            redis0.expire(token, 2592000)
            # g.user = username
            return jsonify({
                'success': True,
                'content': user.nickname,
                'bitmap': user.bitmap
            })
        else:
            return jsonify({
                'success': False,
                'content': 'Wrong Password!',
                'bitmap': None
            })


@app.route('/login_token', methods=['POST'])
def login_token():
    # g.user = None
    token = hashlib.md5(request.form['token']).hexdigest()
    # res = User.query.filter_by(token=token).first()
    if redis0.exists(token):
        res = User.query.filter_by(username=redis0.get(token)).first()
        # g.user = redis0.get(token)
        redis0.expire(token, 2592000)
        return jsonify({
            'success': True,
            'content': res.nickname,
            'bitmap': res.bitmap
        })
    return jsonify({
        'success': False,
        'content': None,
        'bitmap': None
    })


@app.route('/mod_like', methods=['POST'])
def mod_like():
    token = hashlib.md5(request.form['token']).hexdigest()
    if not redis0.exists(token):
        return jsonify({
            'success':False,
            'content':'Could not find user!',
            'like':None,
            'count':None
        })
    videoid_ = request.form['videoid']
    username = redis0.get(token)

    like = Like.query.filter_by(username=username, videoid=videoid_).first()

    if not like:
        like = Like(username, videoid_)
        db.session.add(like)
        db.session.commit()
        count = Like.query.filter_by(videoid=videoid_).count()
        return jsonify({
            'success':True,
            'content':None,
            'like':False,
            'count':count
        })
    db.session.delete(like)
    db.session.commit()
    count = Like.query.filter_by(videoid=videoid_).count()
    return jsonify({
        'success':True,
        'content':None,
        'like': True,
        'count':count
    })



@app.route('/register', methods=['POST'])
def register():
    # g.user = None
    nickname = request.form['nickname']
    username = request.form['username']
    password = hashlib.md5(request.form['password']).hexdigest()
    token = hashlib.md5(request.form['token']).hexdigest()
    if User.query.filter_by(username=username).first():
        return jsonify({
            'success': False,
            'content': 'Username Already Exists!'
        })
    user = User(nickname, username, password)
    db.session.add(user)
    db.session.commit()
    redis0.set(token, username)
    redis0.expire(token, 2592000)
    # g.user = username
    return jsonify({
        'success': True,
        'content': nickname
    })


@app.route('/logout', methods=['POST'])
def logout():
    token = hashlib.md5(request.form['token']).hexdigest()
    redis0.delete(token)
    # g.user = None
    return jsonify({
        'success': True
    })


@app.route('/change', methods=['POST'])
def change():
    nickname = request.form['nickname']
    bitmap = request.form['bitmap']
    password = hashlib.md5(request.form['password']).hexdigest()
    token = hashlib.md5(request.form['token']).hexdigest()
    username = redis0.get(token)
    if bitmap:
        User.query.filter_by(username=username).update({"bitmap": bitmap})
        db.session.commit()
        return jsonify({
            'success': True
        })
    if nickname:
        User.query.filter_by(username=username).update({'nickname': nickname})
        db.session.commit()
        return jsonify({
            'success': True
        })
    if password:
        User.query.filter_by(username=username).update({'password': password})
        db.session.commit()
        return jsonify({
            'success': True
        })




@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        print request.files
        if 'file' not in request.files:
            return jsonify({'success': False, 'content': 'No file part'})
        file_ = request.files['file']
        # if user does not select file, browser also submit a empty part without filename
        if file_.filename == '':
            return jsonify({'success': False, 'content': 'No selected file'})
        else:
            try:
                file_dir = os.getcwd() + '/users'
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                temp = file_.filename.split('+title+')
                title = temp[0]
                temp = temp[1].split('+topic+')
                topic = temp[0]
                temp = temp[1].split('+location+')
                location = temp[0]
                temp = temp[1].split('+token+')
                token = hashlib.md5(temp[0]).hexdigest()
                # filename = secure_filename(file.filename)
                # filename = origin_file_name
                now_time = time.strftime('%Y-%m-%d %X', time.localtime())
                h_path = hashlib.md5(file_.filename.split('.')[0]).hexdigest() + '.' + file_.filename.split('.')[1]
                save_path = os.path.join(file_dir, h_path)

                file_.save(save_path)
                username = redis0.get(token)
                video_ = Video(username, h_path, title, topic, location, False, now_time)
                db.session.add(video_)
                db.session.commit()
                return jsonify({'success': True, 'content': ''})
            except Exception as e:
                return jsonify({'success': False, 'content': 'Error occurred'})
    else:
        return jsonify({'success': False, 'content': 'Method not allowed'})


@app.route('/videoname/<mtoken>', methods=['GET'])
def videoname(mtoken):
    if not Video.query.filter_by(id=1).first():
        return jsonify({
            'content': None,
            'success': False,
            'like': None,
            'count':None
            'videoid': None,
        })
    topic = request.args.get('topic')
    print topic
    token = hashlib.md5(mtoken).hexdigest()
    username = redis0.get(token)
    if redis2.exists(username):
        num = redis2.get(username)
        print redis2.get(username)
        if topic:
            video_ = Video.query.filter(and_(Video.id > num, Video.topic == topic, Video.deleted == False)).limit(1).first()
        else:
            video_ = Video.query.filter(and_(Video.id > num, Video.deleted == False)).limit(1).first()
        if not video_:
            if topic:
                video_ = Video.query.filter(and_(Video.id > 0, Video.topic == topic, Video.deleted == False)).limit(1).first()
            else:
                video_ = Video.query.filter(and_(Video.id > 0, Video.deleted == False)).limit(1).first()
        like = Like.query.filter_by(username=username, videoid=video_.id).first()
        count = Like.query.filter_by(videoid=video_.id).count()
        if not video_:
            return jsonify({
                'content': None,
                'videoid': None,
                'like':False,
                'count':None,
                'success': False,
            })
        redis2.set(username, video_.id)
        redis2.expire(username, 2592000)
        print video_.video
        if not like:
            return jsonify({
                'content': video_.video,
                'like':False,
                'success': True,
                'count':count,
                'videoid': video_.id,
            })
        return jsonify({
            'content': video_.video,
            'videoid': video_.id,
            'success': True,
            'like': True,
            'count': count,
        })
    redis2.set(username, 1)
    redis2.expire(username, 2592000)
    video_ = Video.query.filter_by(id=1).first()
    like = Like.query.filter_by(username=username, videoid=video_.id).first()
    count = Like.query.filter_by(videoid=video_.id).count()
    if not like:
        return jsonify({
            'content': video_.video,
            'like': False,
            'success': True,
            'count':count,
            'videoid': video_.id,
        })
    return jsonify({
        'content': video_.video,
        'like': True,
        'success': True,
        'count':count,
        'videoid': video_.id,
    })


@app.route('/videodetail/<videoid>', methods=['GET'])
def videodetail(videoid):
    video_ = Video.query.filter_by(id=videoid).first()
    user = User.query.filter_by(username=video_.username).first()
    return jsonify({
        'pic': user.bitmap,
        'author': user.nickname,
        'title': video_.title,
        'topic': video_.topic,
        'place': video_.location
    })


@app.route('/video/<filename>', methods=['GET'])
def video(filename):
    dic = os.getcwd() + '/users/'

    def generate():
        with open(dic+filename, 'rb') as f:
            data = f.read(1024)
            while data:
                yield data
                data = f.read(1024)

    return Response(generate(), mimetype="application/octet-stream")


@app.route('/delete', methods=['POST'])
def delete():
    if request.method == 'POST':
        try:
            videoid = request.form['videoid']
            video_ = Video.query.filter_by(id=videoid).first()
            video_.deleted = True
            db.session.commit()
            return jsonify({
                'success': True,
            })
        except Exception as e:
            print(e)
            return jsonify({
                'success': False,
            })


@app.route('/')
def index():
    return "Hello Android Web"


if __name__ == '__main__':
    app.run('0.0.0.0', 80, debug=True)
