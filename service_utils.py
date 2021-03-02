import win32serviceutil
import win32service
import win32event
import logging
import sys
import time
import os

def create_logger(fname):
    logger = logging.getLogger()
    hdlr = logging.FileHandler(fname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger

def get_python():
    return sys.executable.replace("lib\\site-packages\\win32\\PythonService.exe","python.exe")
    import win32api
    import win32con
    key=win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "SOFTWARE", 0, win32con.KEY_ALL_ACCESS)
    key2=win32api.RegCreateKey(key, "Python\\PythonCore\\2.6\\InstallPath")
    return win32api.RegQueryValue(key2,"")+"python.exe"

def get_proc_mem_size(p):
    import os
    pid=str(p.pid)
    tasks=[[i for i in item.split(" ") if i] \
           for item in os.popen("tasklist", "r").read().splitlines() if item][2:]
    for proc in tasks:
        if proc[1]==pid:
            try:
                return int(proc[-2].replace(",",""))
            except:
                return int(proc[-2].replace("\xff",""))
    return 0

def cmd_run(self, hWaitStop, cmd_and_args, path, logger, stop_fun=None):
    from subprocess import Popen
    import os
    import time
    logger.info("\n---1")
    if path: os.chdir(path)
    logger.info("\n---2")
    if callable(cmd_and_args):
        logger.info("\n---3")
        p=cmd_and_args()
    else:
        logger.info("\n---4%s"%cmd_and_args)
        logger.info("\n---4%s"%logger.handlers[0].stream)
        p=Popen(cmd_and_args, stdout=logger.handlers[0].stream)
        logger.info("\n---5")
        logger.info("pid=%s: %s"%(p.pid, " ".join(cmd_and_args)))
        logger.info("\n---6")
    
    # Test if it be stopped!
    while win32event.WAIT_TIMEOUT==win32event.WaitForSingleObject(hWaitStop, 5000):
        if p:
            if p.poll() is not None: #stoped, restart it
                logger.info("%s terminated, restart it"%p.pid)
                if callable(cmd_and_args):
                    p=cmd_and_args()
                else:
                    p=Popen(cmd_and_args, stdout=logger.handlers[0].stream)
                    logger.info("pid=%s: %s"%(p.pid, " ".join(cmd_and_args)))
                time.sleep(10)
            else:
                if self.check_max_log_time:
                    f=logger.handlers[0].stream
                    f.flush()
                    if int(time.time())-os.fstat(f.fileno()).st_mtime>self.check_max_log_time:
                        logger.info("process dead, kill it")
                        if stop_fun:
                            stop_fun(p)
                        p.kill()
                        p.wait()
                        #os.kill(p.pid, signal.SIGTERM)
                        #os.waitpid(p.pid,0)                        
                        time.sleep(10)
                if self.check_max_mem:
                    msize=get_proc_mem_size(p)
                    if msize>self.check_max_mem:
                        logger.info("process memory to large: %dK, kill it", msize)
                        if stop_fun:
                            stop_fun(p)
                        p.kill()
                        p.wait()
                        #os.kill(p.pid, signal.SIGTERM)
                        #os.waitpid(p.pid,0)
                        time.sleep(1)
            
    logger.info("finished")
    if stop_fun:
        stop_fun(p)
    if p:
        p.kill()
        p.wait()
    logger.info(".\n")

class CmdService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DatabaseConnectionPool"
    _svc_display_name_ = "iClock Database Connection Pool Service"
    path = ""
    cmd_and_args=[]
    stop_fun=None
    check_max_log_time=0
    check_max_mem=0
    def init(self, args):
        try:
            win32serviceutil.ServiceFramework.__init__(self, args)
        except Exception, e:
            import traceback; traceback.print_exc()
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        info = os.stat("%smysite/tmp/Svc%s.log"%(self.path and self.path+"/" or "", self._svc_name_))
        if info.st_size > 1024*1024*1024:#Size>10Mb Auto Del 
            os.remove("%smysite/tmp/Svc%s.log"%(self.path and self.path+"/" or "", self._svc_name_))
        self.logger=create_logger("%smysite/tmp/Svc%s.log"%(self.path and self.path+"/" or "", self._svc_name_))
        self.logger.info('----------------%s'%info.st_size)
        self.logger.info('started')
    def __init__(self, args):
        try:
            return self.init(args)
        except:
            import traceback; 
            traceback.print_exc(file=self.logger.handlers[0].stream)
    def SvcStop(self):
        try:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)
            self.logger.info("Send Stop")
        except:
            import traceback; traceback.print_exc(file=self.logger.handlers[0].stream)
            
    def SvcDoRun(self):
        self.logger.info("Running")
        try:
            self.run(self.cmd_and_args)
        except Exception, e:
            import traceback; traceback.print_exc(file=self.logger.handlers[0].stream)
    def run(self, cmd_and_args):
        return cmd_run(self, self.hWaitStop, cmd_and_args, self.path, self.logger, self.stop_fun)

class PythonService(CmdService):
    def run(self, cmd_and_args):
        python=get_python()
        if self.logger: self.logger.info("python: %s"%python)
        return CmdService.run(self, [python,]+cmd_and_args)
        
class DjangoService(PythonService):
    def run(self, cmd_and_args):
        return PythonService.run(self, ["manage.py",]+cmd_and_args)

def main(ServiceClass):
    import sys
    if len(sys.argv)>1:
        win32serviceutil.HandleCommandLine(ServiceClass)
    else:
        r=ServiceClass([ServiceClass._svc_name_])
        r.run(ServiceClass.cmd_and_args)

