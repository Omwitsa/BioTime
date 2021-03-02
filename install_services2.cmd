call init.bat
sc stop iclock-server
sc delete iclock-server
python ServiceWriteData.py  --startup auto install
python ServiceQueqe.py  --startup auto install
python ServiceMemCached.py  --startup auto install
net start iClockMemCachedService
net start iClockQueueService
net start iClockWriteDataService