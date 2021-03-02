"""Microsoft SQL Server database backend for Django."""
from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseValidation, BaseDatabaseClient
from django.db.backends.signals import connection_created
from django.core.exceptions import ImproperlyConfigured

import dbapi as Database

from introspection import DatabaseIntrospection
from creation import DatabaseCreation
from operations import DatabaseOperations

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError

class DatabaseFeatures(BaseDatabaseFeatures):
    uses_custom_query_class = True
    can_use_chunked_reads = False
# IP Address recognizer taken from:
# http://mail.python.org/pipermail/python-list/2006-March/375505.html
def _looks_like_ipaddress(address):
    dots = address.split(".")
    if len(dots) != 4:
        return False
    for item in dots[:-1]:
        if not 0 <= int(item) <= 255:
            return False
    if dots[-1].find("\SQLEXPRESS")!=-1:
        if not 0 <= int(dots[-1].split("\\")[0]) <= 255:
            return False
    else:
        return True
        if not 0 <= int(dots[-1]) <= 255:
            return False
        
    return True

def connection_string_from_settings():
    from django.conf import settings
    return make_connection_string(settings)

def make_connection_string(settings):
    class wrap(object):
        def __init__(self, mapping):
            self._dict = mapping
            
        def __getattr__(self, name):
            d = self._dict
            result = None
            if hasattr(d, "get"):
                if d.has_key(name):
                    result = d.get(name)
                else:
                    result = d.get('DATABASE_' + name)
            elif hasattr(d, 'DATABASE_' + name):
                result = getattr(d, 'DATABASE_' + name)
            else:
                result = getattr(d, name)
            return result
            
    settings = wrap(settings)
    
    db_name = settings.NAME.strip()
    db_host = settings.HOST or '127.0.0.1'
    if len(db_name) == 0:
        raise ImproperlyConfigured("You need to specify a DATABASE NAME in your Django settings file.")

    # Connection strings courtesy of:
    # http://www.connectionstrings.com/?carrier=sqlserver
    # If a port is given, force a TCP/IP connection. The host should be an IP address in this case.
    if settings.PORT != '' and settings.PORT!="1433":
        if not _looks_like_ipaddress(db_host):
            raise ImproperlyConfigured("When using DATABASE PORT, DATABASE HOST must be an IP address.")
        datasource = '{host},{port};Network Library=DBMSSOCN'.format(
            host=db_host,
            port=settings.PORT
        )

    # If no user is specified, use integrated security.
    if settings.USER != '':
        auth_string = "UID={user};PWD={password}".format(
            user=settings.USER,
            password=settings.PASSWORD
        )
    else:
        auth_string = "Integrated Security=SSPI"

    parts = [
        "PROVIDER=SQLOLEDB", 
        "DATA SOURCE={0}".format(db_host+','+str(settings.PORT)),
        "Initial Catalog={0}".format(db_name),
        auth_string
    ]
    
    options = settings.OPTIONS
    if options:
        if 'use_mars' in options and options['use_mars']:
            parts.append("MultipleActiveResultSets=true")
            
        if 'extra_params' in options:
            parts.append(options['extra_params'])
        
        if 'provider' in options:
            parts[0] = 'PROVIDER={0}'.format(options['provider'])
    
    return ";".join(parts)

class DatabaseWrapper(BaseDatabaseWrapper):
    operators = {
        "exact": "= %s",
        "iexact": "LIKE %s ESCAPE '\\'",
        "contains": "LIKE %s ESCAPE '\\'",
        "icontains": "LIKE %s ESCAPE '\\'",
        "gt": "> %s",
        "gte": ">= %s",
        "lt": "< %s",
        "lte": "<= %s",
        "startswith": "LIKE %s ESCAPE '\\'",
        "endswith": "LIKE %s ESCAPE '\\'",
        "istartswith": "LIKE %s ESCAPE '\\'",
        "iendswith": "LIKE %s ESCAPE '\\'",
    }

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        
        self.features = DatabaseFeatures()
        self.ops = DatabaseOperations()
        
        self.client = BaseDatabaseClient(self)
        self.creation = DatabaseCreation(self) 
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation(self)

        self.command_timeout = getattr(self.settings_dict, 'COMMAND_TIMEOUT', 30)
        if type(self.command_timeout) != int:
            self.command_timeout = 30
        
    def _cursor(self):
        if self.connection is None:
            self.connection = Database.connect(
                                make_connection_string(self.settings_dict),
                                self.command_timeout
                              )
            connection_created.send(sender=self.__class__)

        return Database.Cursor(self.connection)
