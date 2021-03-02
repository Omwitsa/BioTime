
echo "Starting ADMS Server Manager...."
ping -n 5 127.1>nul
start /min "Starting" "%cd%\iClockMng.exe" "/m"
start /min "Starting" "C:\iclocksvr\iClockMng.exe" "/m"
exit