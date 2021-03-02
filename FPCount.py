# -*- coding: utf-8 -*-

startDate = "2010-09-08 09:00"
endDate = "2010-09-08 22:00"

from django.db import connection
cursor = connection.cursor()
sqls="select * from devcmds where (locate('DATA FP PIN',CmdContent) > 0 or locate('DATA UPDATE FINGERTMP PIN',CmdContent) > 0) and (CmdCommitTime>='%s' and CmdCommitTime<='%s') "%(startDate,endDate)

sql=sqls+" and CmdReturn=0"
num = cursor.execute(sql)


sql=sqls+" and CmdReturn!=0"
num1 = cursor.execute(sql) 
results = cursor.fetchall()


sql=sqls+" and CmdReturn is null"
num2 = cursor.execute(sql)


numAll = cursor.execute(sqls)

sql2 = sqls.replace("DATA FP PIN","DATA USER PIN").replace("FINGERTMP","USERINFO")
num_u= cursor.execute(sql2)
num_u2= cursor.execute(sql2+" and CmdReturn=0")
num_u3= cursor.execute(sql2+" and (CmdReturn!=0 or CmdReturn is null)")
results2 = cursor.fetchall()

print u'执行成功的指纹模板数 =',num
print u'执行不成功的指纹模板数 =',num1,u'(not 0) ',num2,u'(is null)'
print u'指纹模板总数 =',numAll 
print u'用户人员总数 =',num_u
print u'执行成功的用户人员数 =',num_u2
print u'执行不成功的用户人员数 =',num_u3

#connection._commit()

lines = ""
if results:
    for r in results:
        lines += str(r) + "\n"
if lines:
    import datetime
    dt = str(datetime.datetime.now())[:10]
    f = file('tmp\FailDevcmdsOfTMP%s.txt'%dt,'a')
    f.write(lines + '\n')
    f.close()

lines = ""
if results2:
    for r in results2:
        lines += str(r) + "\n"
if lines:
    import datetime
    dt = str(datetime.datetime.now())[:10]
    f = file('tmp\FailDevcmdsOfUser%s.txt'%dt,'a')
    f.write(lines + '\n')
    f.close()