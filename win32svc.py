"""
The most basic (working) CherryPy 3.0 Windows service possible.
Requires Mark Hammond's pywin32 package.
"""
from svr8000 import loadServer
import win32serviceutil
import win32service
import win32event
import sys
from mysite.utils import *
import servicemanager

class MyService(win32serviceutil.ServiceFramework):
	"""NT Service."""
	
	_svc_name_ = "AttServer"
	_svc_display_name_ = "iClock ADMS Service"

	def __init__(self, args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		# create an event that SvcDoRun can wait on and SvcStop
		# can set.
		servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, 'init (%s)(sys.path=%s)' % self._svc_display_name_, sys.path))
		self.stop_event = win32event.CreateEvent(None, 0, 0, None)

	def SvcDoRun(self):
		servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, 'start (%s)(sys.path=%s)' % self._svc_display_name_, sys.path))
		self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
		self.server=loadServer()
		self.ReportServiceStatus(win32service.SERVICE_RUNNING)
		self.server.start()
#		print "now, block until our event is set..."
		win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
	
	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		self.server.stop()
		win32event.SetEvent(self.stop_event)
		self.ReportServiceStatus(win32service.SERVICE_STOPPED)

if __name__ == '__main__':
	win32serviceutil.HandleCommandLine(MyService)

