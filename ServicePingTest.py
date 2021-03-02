from service_utils import main, DjangoService
import os
import sys


path=os.path.split(__file__)[0]

class WriteDataService(DjangoService):
    _svc_name_ = "iClockSyncQueueService"
    _svc_display_name_ = "iClock Sync Queue Service"
    #_svc_deps_ = ["iClockMemCachedService", "iClockQueueService"]
    #_svc_deps_ = ["iClockQueueService"]
    path = path
    cmd_and_args=["syncqueue"]
    check_max_log_time=15*60
    check_max_mem = 300*1024
    
if __name__=='__main__':
    main(WriteDataService)
    