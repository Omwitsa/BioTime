@echo off
call init.bat
echo Server Starting ... ...
for /L %%i IN (0,1,2000) DO python svr8000.py