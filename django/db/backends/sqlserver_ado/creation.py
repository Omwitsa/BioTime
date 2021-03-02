# This dictionary maps Field objects to their associated Server Server column
# types, as strings. Column-type strings can contain format strings; they'll
# be interpolated against the values of Field.__dict__.
from django.conf import settings
from django.db.backends.creation import BaseDatabaseCreation, TEST_DATABASE_PREFIX
import sys

class DatabaseCreation(BaseDatabaseCreation):
    data_types = {
        'AutoField':            'int IDENTITY (1, 1)',
        'BigAutoField':         'bigint IDENTITY (1, 1)',
        'BigIntegerField':      'bigint',
        'BooleanField':         'bit',
        'CharField':            'nvarchar(%(max_length)s)',
        'CommaSeparatedIntegerField': 'nvarchar(%(max_length)s)',
        'DateField':            'datetime',
        'DateTimeField':        'datetime',
        'DecimalField':         'decimal(%(max_digits)s, %(decimal_places)s)',
        'FileField':            'nvarchar(%(max_length)s)',
        'FilePathField':        'nvarchar(%(max_length)s)',
        'FloatField':           'double precision',
        'IntegerField':         'int',
        'IPAddressField':       'nvarchar(15)',
        'NullBooleanField':     'bit',
        'OneToOneField':        'int',
        'PositiveIntegerField': 'int CHECK ([%(column)s] >= 0)',
        'PositiveSmallIntegerField': 'smallint CHECK ([%(column)s] >= 0)',
        'SlugField':            'nvarchar(%(max_length)s)',
        'SmallIntegerField':    'smallint',
        'TextField':            'nvarchar(max)',
        'TimeField':            'datetime',
    }

    def _disable_transactions(self, verbosity=1):
        """Temporarily turn off transactions for non-transactionable SQL"""
        if self.connection.connection.supportsTransactions:
            if verbosity >= 1:
                print "Disabling Transactions"
            self._supports_transactions = self.connection.connection.supportsTransactions
            self.connection._commit()
            self.connection.connection.supportsTransactions = False

    def _reenable_transactions(self, verbosity=1):
        """Reset transaction support to state prior to _disable_transactions() call"""
        if hasattr(self, '_supports_transactions'):
            if verbosity >= 1:
                print "Re-enabling Transactions"
            self.connection.connection.supportsTransactions = self._supports_transactions

    def _create_test_db(self, verbosity=1, autoclobber=False):
        test_database_name = self._test_database_name(settings)
        
        if not self._test_database_create(settings):
            if verbosity >= 1:
                print "Skipping Test DB creation"
            return test_database_name

        # Create the test database and connect to it. We need to autocommit
        # if the database supports it because PostgreSQL doesn't allow
        # CREATE/DROP DATABASE statements within transactions.
        cursor = self.connection.cursor()
        suffix = self.sql_table_creation_suffix()
        qn = self.connection.ops.quote_name

        try:
            self._disable_transactions()
            cursor.execute("CREATE DATABASE %s %s" % (qn(test_database_name), suffix))
            self._reenable_transactions()
        except Exception, e:
            sys.stderr.write("Got an error creating the test database: %s\n" % e)
            if not autoclobber:
                confirm = raw_input("Type 'yes' if you would like to try deleting the test database '%s', or 'no' to cancel: " % test_database_name)
            if autoclobber or confirm == 'yes':
                try:
                    self._disable_transactions()
                    if verbosity >= 1:
                        print "Destroying old test database..."
                    cursor.execute("DROP DATABASE %s" % qn(test_database_name))
                    if verbosity >= 1:
                        print "Creating test database..."
                    cursor.execute("CREATE DATABASE %s %s" % (qn(test_database_name), suffix))
                    self._reenable_transactions()
                except Exception, e:
                    sys.stderr.write("Got an error recreating the test database: %s\n" % e)
                    sys.exit(2)
            else:
                print "Tests cancelled."
                sys.exit(1)

        return test_database_name
        

    def _destroy_test_db(self, test_database_name, verbosity=1):
        "Internal implementation - remove the test db tables."

        if self._test_database_create(settings):
            qn = self.connection.ops.quote_name

            # Remove the test database to clean up after
            # ourselves. Connect to the previous database (not the test database)
            # to do so, because it's not allowed to delete a database while being
            # connected to it.
            cursor = self.connection.cursor()
            self.set_autocommit()
            import time
            time.sleep(1) # To avoid "database is being accessed by other users" errors.
            self._disable_transactions()
            cursor.execute("DROP DATABASE %s" % self.connection.ops.quote_name(test_database_name))
            self._reenable_transactions()
            self.connection.close()
        else:
            print "Skipping Test DB destruction"    
        
    def _test_database_create(self, settings):
        if hasattr(settings, 'TEST_DATABASE_CREATE'):
            return settings.TEST_DATABASE_CREATE
        else:
            return True

    def _test_database_name(self, settings):
        if hasattr(settings, 'TEST_DATABASE_NAME') and settings.TEST_DATABASE_NAME:
            return settings.TEST_DATABASE_NAME
        else:
            return TEST_DATABASE_PREFIX + settings.DATABASE_NAME
