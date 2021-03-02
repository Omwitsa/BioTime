call init.bat
sc stop iclock-server
sc delete iclock-server
python ServiceADMS.py --startup auto install
python ServiceWriteData.py  --startup auto install
python ServiceQueqe.py  --startup auto install
python ServiceMemCached.py  --startup auto install
python ServiceMng1.py  --startup auto install
python ServiceMng4.py  --startup auto install
net start iClockMemCachedService
net start iClockQueueService
net start iClockWriteDataService
net start iClockMng1
net start iClockMng4
net start AttServer