if {%1}=={} GOTO noparms
set p=%1\
goto param1

:noparms
set p=%CD%\

:param1
call %p%init.bat %p%


IF EXIST %p%mysite\tasks.py GOTO py
 
python.exe %p%mysite\tasks.pyc weekly
GOTO end

:py
python.exe %p%mysite\tasks.py weekly

:end

