"""Microsoft SQL Server database backend for Django."""
from django.db.backends.sqlserver_pool.bdwrapper import NativeDatabaseWrapper
from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseValidation, BaseDatabaseClient
from django.db.backends.signals import connection_created
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.db.backends.sqlserver_ado import dbapi as Database


#/*********sqlserver pool start pwp***********/
from django.db.backends.sqlserver_ado.base import DatabaseFeatures,DatabaseOperations,make_connection_string,connection_string_from_settings
pool_wait = 28800
pool_size = 20
pool_max = 100
pool_giveup = 10

try:
    pool_wait = settings.DBPOOL_WAIT_TIMEOUT
    pool_size = settings.DBPOOL_SIZE
    pool_max = settings.DBPOOL_MAX
    poll_giveup = settings.DBPOOL_INTERNAL_CONN_TIMEOUT
except ImportError:
    print(u"Please define DBPOOL_WAIT_TIMEOUT, DBPOOL_SIZE, DBPOOL_MAX, DBPOOL_INTERNAL_CONN_TIMEOUT in your settings file.")

try:
    DEBUG = settings.DEBUG
except:
    DEBUG = False
    
try:
    from django.db.backends.sqlserver_pool.pool import manage, QueuePool
except ImportError:
    import traceback;traceback.print_exc();

Database = manage(Database, 
                  echo = DEBUG,
                  poolclass = QueuePool,
                  recycle = pool_wait, 
                  pool_size = pool_size, 
                  max_overflow = pool_max,
                  timeout = pool_giveup
)
#/*********sqlserver pool end pwp***********/


class DatabaseWrapper(NativeDatabaseWrapper):

    def _cursor(self):
        if self.connection is None:
            self.connection = Database.connect(
                                make_connection_string(self.settings_dict),
                                self.command_timeout
                              )
            connection_created.send(sender=self.__class__)
        #print  Database.Cursor(self.connection)
        return Database.Cursor(self.connection)
    