from service_utils import main, PythonService
import os
import sys
import redis
from subprocess import Popen

path=os.path.split(__file__)[0]

class iClockADMSService(PythonService):
    _svc_name_ = "AttServer"
    _svc_display_name_ = "iClock ADMS Service"
    _svc_deps_ = ["iClockMemCachedService","iClockQueueService","iClockWriteDataService","iClockMng1","iClockMng4"]
    path = path
    cmd_and_args=["svr8000.py",]
    #cmd_and_args=WORK_PATH+'.\svr8000.py'
    print"cmd_and_args----",cmd_and_args
    check_max_mem=1024*1024
    def stop_fun(self, process):
        os.system("""taskkill /IM nginx.exe /F""")

if __name__=='__main__':
    main(iClockADMSService)
    
