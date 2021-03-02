# -*- coding: utf-8 -*-
from service_utils import main, CmdService
import os
import sys
import redis
from subprocess import Popen
from mysite import settings
redisport = int(settings.REDIS_PORT)
redispwd = settings.REDIS_PWD

path=os.path.split(__file__)[0]

def start_q_server(stdout=None):
    exe_name=redis.__path__[0]+"/redis-server"
    if not os.name=='posix': exe_name+=".exe"
    return Popen(exe_name, stdout=stdout)

class QueueService(CmdService):
    _svc_name_ = "iClockQueueService"
    _svc_display_name_ = "iClock Queue Service"
    path = path
    #cmd_and_args="\"\"%s/redis-server.exe %s/redis.conf\"\"" %(redis.__path__[0],redis.__path__[0])
    redis_server_path = redis.__path__[0]+"\\redis-server.exe"
    redis_conf_path =redis.__path__[0]+"\\redis.conf"
    cmd_and_args=[redis_server_path,]+[redis_conf_path,]#解决redis路径中包含空格导致不能调用的bug  By Bosco
    def stop_fun(self, process):
        if not process: return
        q=redis.Redis(host='localhost', port=redisport, db=0, password=redispwd)
        q.save()
    
if __name__=='__main__':
    main(QueueService)
    