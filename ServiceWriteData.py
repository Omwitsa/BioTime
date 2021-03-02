from service_utils import main, DjangoService
import os
import sys


path=os.path.split(__file__)[0]

class WriteDataService(DjangoService):
    _svc_name_ = "iClockWriteDataService"
    _svc_display_name_ = "iClock Write Data Service"
    #_svc_deps_ = ["iClockMemCachedService", "iClockQueueService"]
    _svc_deps_ = ["iClockQueueService"]
    path = path
    cmd_and_args=["writedata"]
    check_max_log_time=15*60
    check_max_mem = 300*1024
    
if __name__=='__main__':
    main(WriteDataService)
    