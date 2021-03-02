cls
@echo off
call init.bat

if EXIST mysql call installmysql.bat

if NOT EXIST memcached.exe GOTO n
echo "Install memcached ..."
sc create memcached binPath= "%CD%\memcached.exe -p 11211 -l 127.0.0.1 -m 128 -d runservice" DisplayName= "memcached server" start= auto depend= TCPIP
net start memcached
:n

echo creating initialize database ...
python mysite\manage.py syncdb

echo.
echo iclock server is now ready, please run svr8000.exe to start.
echo.
