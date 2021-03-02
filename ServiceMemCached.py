from service_utils import main, CmdService
import os
import sys
import redis
from subprocess import Popen

path=os.path.split(__file__)[0]

class MemCachedService(CmdService):
    _svc_name_ = "iClockMemCachedService"
    _svc_display_name_ = "iClock MemCached Service"
    path = path
    cmd_and_args=["memcached.exe",  "-p 11211 -l 127.0.0.1 -m 128"]
    
if __name__=='__main__':
    main(MemCachedService)
    