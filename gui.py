# -*- coding: utf-8 -*-

import win32api, win32gui  
import win32con, winerror  
import sys, os  

def is_service_stoped():
    s=os.popen("sc.exe query AttServer").read()
    print"--st:",s
    #if ": 1  STOPPED" in s:
    if "RUNNING" in s:
        return False
    return True

class MainWindow:  
    def __init__(self):  
        msg_TaskbarRestart = win32gui.RegisterWindowMessage("TaskbarCreated");
        message_map = {
                msg_TaskbarRestart: self.OnRestart,
                win32con.WM_DESTROY: self.OnDestroy,
                win32con.WM_COMMAND: self.OnCommand,
                win32con.WM_USER+20 : self.OnTaskbarNotify,
        }
        # Register the Window class.  
        wc = win32gui.WNDCLASS()  
        hinst = wc.hInstance = win32api.GetModuleHandle(None)  
        wc.lpszClassName = "iClockTaskbar"  
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;  
        wc.hCursor = win32api.LoadCursor( 0, win32con.IDC_ARROW )  
        wc.hbrBackground = win32con.COLOR_WINDOW  
        wc.lpfnWndProc = message_map # could also specify a wndproc.  
  
        # Don't blow up if class already registered to make testing easier  
        try:  
            classAtom = win32gui.RegisterClass(wc)  
        except win32gui.error, err_info:  
            if err_info.winerror!=winerror.ERROR_CLASS_ALREADY_EXISTS:  
                raise
  
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU  
        self.hwnd = win32gui.CreateWindow( wc.lpszClassName, "Taskbar iClock", style,  
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 
                0, 0, hinst, None)  
        win32gui.UpdateWindow(self.hwnd)  
        self._DoCreateIcons()  
    def _DoCreateIcons(self):  
        # Try and find a custom icon  
        hinst =  win32api.GetModuleHandle(None)  
        print"---icon"
        iconPathName = "mysite\\favicon.ico"
        print"---icon2"
        if os.path.isfile(iconPathName):  
            print"---icon3"
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE  
            hicon = win32gui.LoadImage(hinst, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)  
        else:  
            print "Can't find a Python icon file - using default"  
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)  
  
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP  
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, u"iClock Server 服务控制器")  
        try:  
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)  
        except win32gui.error:  
            # This is common when windows is starting, and this code is hit  
            # before the taskbar has been created.  
            print "Failed to add the taskbar icon - is explorer running?"  
            # but keep running anyway - when explorer starts, we get the  
            # TaskbarCreated message.  
  
    def OnRestart(self, hwnd, msg, wparam, lparam):
        print"--creaticon"  
        self._DoCreateIcons()  
  
    def OnDestroy(self, hwnd, msg, wparam, lparam):  
        nid = (self.hwnd, 0)  
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)  
        win32gui.PostQuitMessage(0) # Terminate the app.  
  
    def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):  
        if lparam==win32con.WM_LBUTTONUP:  
            print u"单击了一下."  
        elif lparam==win32con.WM_LBUTTONDBLCLK:  
            print u"双击了一下"  
            win32gui.DestroyWindow(self.hwnd)  
        elif lparam==win32con.WM_RBUTTONUP:  
            menu = win32gui.CreatePopupMenu()
            if is_service_stoped():
                win32gui.AppendMenu( menu, win32con.MF_STRING, 1023, u"iClock 服务没有运行. 点击此处启动运行")
            else:
                win32gui.AppendMenu( menu, win32con.MF_STRING, 1023, u"iClock 服务正在运行，点击此处停止运行 ")  
            #win32gui.AppendMenu( menu, win32con.MF_STRING, 1024, "Check iClock ADMS server status")  
            win32gui.AppendMenu( menu, win32con.MF_STRING, 1025, u"退出 iClock Server 服务控制器" )
            pos = win32gui.GetCursorPos()  
            win32gui.SetForegroundWindow(self.hwnd)  
            win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)  
            win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)  
        return 1  
  
    def OnCommand(self, hwnd, msg, wparam, lparam):  
        id = win32api.LOWORD(wparam)  
        if id == 1023:  #Start iclock ADMS server
            if is_service_stoped():
                os.system("net start iClockMemCachedService")
                os.system("net start iClockQueueService")
                os.system("net start iClockWriteDataService")
                os.system("net start AttServer")
            else:
                os.system("net stop AttServer")
                os.system("net stop iClockMemCachedService")
                os.system("net stop iClockWriteDataService")
                os.system("net stop iClockQueueService")
            #os.system("net stop iClockWriteDataService")
            #os.system("net stop iClockQueqeService")
        elif id == 1024: #Check iclock ADMS server status 
            print "Hello"
        elif id == 1025: # 
            print "Goodbye"
            win32gui.DestroyWindow(self.hwnd)
        else:
            print "Unknown command -", id
  
def main(): 
    #os.system("runas /profile /user:mymachine\\administrator \"C:\iclockSvr\Python26\pythonw.exe C:\iclockSvr\gui.py\"")
    w=MainWindow()  
    win32gui.PumpMessages()  
  
if __name__=='__main__':  
    main()  

