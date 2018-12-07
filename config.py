#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
# import importlib # for Python3x

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
#    importlib.reload(sys) # for Python3x
    reload(sys)
    sys.setdefaultencoding(default_encoding)

USER = 'root'
PASSWORD = '12345678'
URL = 'localhost'
PORT = '3306'
DATABASE = 'project'
UPLOAD_PATH = 'users'
