from service_utils import main, PythonService
import os
import sys
import redis
from subprocess import Popen

path=os.path.split(__file__)[0]

class iClockADMSService(PythonService):
    _svc_name_ = "iClockMng4"
    _svc_display_name_ = "iClock Mng4 Service"
    #_svc_deps_ = ["iClockMemCachedService","iClockQueueService","iClockWriteDataService"]
    path = path
    cmd_and_args=["svr8004.py",]
    #cmd_and_args=WORK_PATH+'.\svr8001.py'
    print"cmd_and_args----",cmd_and_args
    check_max_mem=1024*1024
    def stop_fun(self, process):
        os.system("""taskkill /IM nginx.exe /F""")

if __name__=='__main__':
    main(iClockADMSService)
    
