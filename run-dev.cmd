call init.bat
echo Server Starting ... ...
@for /L %%i IN (0,1,2000) DO @python %PRJ_NAME%\manage.py runserver 0.0.0.0:8081