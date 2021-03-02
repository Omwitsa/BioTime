# -*- coding: utf-8 -*-

import win32api, win32gui  
import win32con, winerror  
import sys, os  

def main():  
    os.system("runas /profile /user:mymachine\\administrator \"C:\iclockSvr\Python26\pythonw.exe C:\iclockSvr\gui.py\"")
    #win32gui.DestroyWindow(self.hwnd)
  
if __name__=='__main__':  
    main()  

