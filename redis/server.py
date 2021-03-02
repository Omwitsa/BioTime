# -*- coding: utf-8 -*-

import os, time
import redis
from subprocess import Popen

from mysite import settings
redisport = int(settings.REDIS_PORT)
redispwd = settings.REDIS_PWD

def start_q_server():
	f=file("redis.log","a+")
	exe_name=os.path.split(__file__)[0]+"/redis-server"
	if not os.name=='posix': exe_name+=".exe"
	print "start", exe_name
	Popen(exe_name, stdout=f)
	time.sleep(2)

def queqe_server(q=None):
    return q or redis.Redis(host='localhost', port=redisport, db=0, password=redispwd)
    """try:
        q.ping()
    except redis.exceptions.InvalidResponse:
        print "InvalidResponse while queqe_server"
    except redis.exceptions.ConnectionError: 
        print "ConnectionError while queqe_server"
    return q"""

def check_and_start_queqe_server(q=None):
	q=q or redis.Redis(host='localhost', port=redisport, db=0, password=redispwd)
	try:
		q.ping()
	except redis.exceptions.ConnectionError: 
		start_q_server()
	except redis.exceptions.InvalidResponse:
		pass
	return q
    
