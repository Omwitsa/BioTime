#!/usr/bin/python
from redis.server import queqe_server 

def test(c):
    q=queqe_server()
    i=0
    while i<c:
        name="k%s"%i
        value=("v%s"%i)*10
        q.set(name, value)
        i+=1
    i=0
    while i<c:
        name="k%s"%i
        value=("v%s"%i)*10
        v=q.get(name)
        if not (v==value):
            print "ERROR", v, value
        i+=1
    i=0
    while i<c:
        name="k%s"%i
        q.delete(name, value)
        i+=1

if __name__=="__main__":
    test(10000)


