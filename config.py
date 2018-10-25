#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

USER = 'root'
PASSWORD = '123456'
URL = 'localhost'
PORT = '3306'
DATABASE = 'project'
UPLOAD_PATH = 'users'
