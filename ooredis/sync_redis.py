# -*- coding: utf-8 -*-

def get_info():
    '''Returns a dictionary containing information about the Redis server'''
    from ooredis import get_client
    cl = get_client()
    return cl.info()

def get_dbsize():
    '''Returns the number of keys in the current database'''
    from ooredis import get_client
    cl = get_client()
    return cl.dbsize()

def save_db():
    from ooredis import get_client
    cl = get_client()
    cl.save()
    
def bgsave():
    from ooredis import get_client
    cl = get_client()
    cl.bgsave()
    
def shutdown():
    from ooredis import get_client
    cl = get_client()
    cl.shutdown()
    
def safe_exit():
    from ooredis import get_client
    cl = get_client()
    cl.save()
    cl.shutdown()
    
def lastsave():
    from ooredis import get_client
    cl = get_client()
    return cl.lastsave()

def get_all_keys():
    from ooredis import get_client
    cl = get_client()
    return cl.keys()

def cleandb():
    from ooredis import get_client
    cl = get_client()
    cl.flushdb()