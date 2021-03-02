call init.bat
@for /L %%i IN (0,1,2000) DO python.exe manage.py writedata
pause

