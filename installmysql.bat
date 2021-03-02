echo installing mysql database server ...
cd mysql
"%CD%\bin\mysqld.exe" --install iclock-data --defaults-file="%CD%\my.ini"
net start iclock-data
cd ../
