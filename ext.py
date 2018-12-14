#!/usr/bin/python
# -*- coding:utf-8 -*-
import redis
import sys
# import importlib #for Python 3x

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    #importlib.reload(sys) #for Python 3x
    reload(sys)
    sys.setdefaultencoding(default_encoding)

redis0 = redis.StrictRedis(host='localhost', port=6379, db=0)
redis1 = redis.StrictRedis(host='localhost', port=6379, db=1)
redis2 = redis.StrictRedis(host='localhost', port=6379, db=2)
