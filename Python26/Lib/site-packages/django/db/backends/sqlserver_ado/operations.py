from django.db.backends import BaseDatabaseOperations
import datetime
import time


class DatabaseOperations(BaseDatabaseOperations):
    compiler_module = "sqlserver_ado.compiler"
    
    def date_extract_sql(self, lookup_type, field_name):
        return "DATEPART(%s, %s)" % (lookup_type, self.quote_name(field_name))

    def date_trunc_sql(self, lookup_type, field_name):
    	quoted_field_name = self.quote_name(field_name)

        if lookup_type == 'year':
            return "Convert(datetime, Convert(varchar, DATEPART(year, %s)) + '/01/01')" % quoted_field_name

        if lookup_type == 'month':
            return "Convert(datetime, Convert(varchar, DATEPART(year, %s)) + '/' + Convert(varchar, DATEPART(month, %s)) + '/01')" %\
                (quoted_field_name, quoted_field_name)

        if lookup_type == 'day':
            return "Convert(datetime, Convert(varchar(12), %s))" % quoted_field_name

    def last_insert_id(self, cursor, table_name, pk_name):
        cursor.execute("SELECT CAST(IDENT_CURRENT(%s) as bigint)", [self.quote_name(table_name)])
        return cursor.fetchone()[0]

    def no_limit_value(self):
        return None

    def prep_for_like_query(self, x):
        """Prepares a value for use in a LIKE query."""
        from django.utils.encoding import smart_unicode
        return (
            smart_unicode(x).\
                replace("\\", "\\\\").\
                replace("%", "\%").\
                replace("_", "\_").\
                replace("[", "\[").\
                replace("]", "\]")
            )

    def quote_name(self, name):
        if name.startswith('[') and name.endswith(']'):
            return name # already quoted
        return '[%s]' % name

    def random_function_sql(self):
        return 'RAND()'

    def regex_lookup(self, lookup_type):
        # Case sensitivity
        match_option = {'iregex':0, 'regex':1}[lookup_type]
        return "dbo.REGEXP_LIKE(%%s, %%s, %s)=1" % (match_option,)

    def sql_flush(self, style, tables, sequences):
        """
        Returns a list of SQL statements required to remove all data from
        the given database tables (without actually removing the tables
        themselves).

        The `style` argument is a Style object as returned by either
        color_style() or no_style() in django.core.management.color.
        
        Originally taken from django-pyodbc project.
        """
        if not tables:
            return list()
            
        qn = self.quote_name
            
        # Cannot use TRUNCATE on tables that are referenced by a FOREIGN KEY; use DELETE instead.
        # (which is slow)
        from django.db import connection
        cursor = connection.cursor()
        # Try to minimize the risks of the braindeaded inconsistency in
        # DBCC CHEKIDENT(table, RESEED, n) behavior.
        seqs = []
        for seq in sequences:
            cursor.execute("SELECT COUNT(*) FROM %s" % qn(seq["table"]))
            rowcnt = cursor.fetchone()[0]
            elem = dict()

            if rowcnt:
                elem['start_id'] = 0
            else:
                elem['start_id'] = 1

            elem.update(seq)
            seqs.append(elem)

        cursor.execute("SELECT TABLE_NAME, CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_TYPE IN ('CHECK', 'FOREIGN KEY')")
        fks = cursor.fetchall()
        
        sql_list = list()

        # Turn off constraints.
        sql_list.extend(['ALTER TABLE %s NOCHECK CONSTRAINT %s;' % (
            qn(fk[0]), qn(fk[1])) for fk in fks if fk[0] is not None and fk[1] is not None])

        # Delete data from tables.
        sql_list.extend(['%s %s %s;' % (
            style.SQL_KEYWORD('DELETE'), 
            style.SQL_KEYWORD('FROM'), 
            style.SQL_FIELD(qn(t))
            ) for t in tables])

        # Reset the counters on each table.
        sql_list.extend(['%s %s (%s, %s, %s) %s %s;' % (
            style.SQL_KEYWORD('DBCC'),
            style.SQL_KEYWORD('CHECKIDENT'),
            style.SQL_FIELD(qn(seq["table"])),
            style.SQL_KEYWORD('RESEED'),
            style.SQL_FIELD('%d' % seq['start_id']),
            style.SQL_KEYWORD('WITH'),
            style.SQL_KEYWORD('NO_INFOMSGS'),
            ) for seq in seqs])

        # Turn constraints back on.
        sql_list.extend(['ALTER TABLE %s CHECK CONSTRAINT %s;' % (
            qn(fk[0]), qn(fk[1])) for fk in fks if fk[0] is not None and fk[1] is not None])

        return sql_list

    def tablespace_sql(self, tablespace, inline=False):
        return "ON %s" % self.quote_name(tablespace)
        
    def value_to_db_datetime(self, value):
        if value is None:
            return None
            
        if value.tzinfo is not None:
            raise ValueError("SQL Server 2005 does not support timezone-aware datetimes.")

        # SQL Server 2005 doesn't support microseconds
        return value.replace(microsecond=0)
    
    def value_to_db_time(self, value):
        # MS SQL 2005 doesn't support microseconds
        #...but it also doesn't really suport bare times
        if value is None:
            return None
        return value.replace(microsecond=0)
	        
    def value_to_db_decimal(self, value, max_digits, decimal_places):
        if value is None or value == '':
            return None
        return value # Should be a decimal type (or string)

    def year_lookup_bounds(self, value):
        """
        Returns a two-elements list with the lower and upper bound to be used
        with a BETWEEN operator to query a field value using a year lookup

        `value` is an int, containing the looked-up year.
        """
        first = '%s-01-01 00:00:00'
        second = '%s-12-31 23:59:59'
        return [first % value, second % value]
