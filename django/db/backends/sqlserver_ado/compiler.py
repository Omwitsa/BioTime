from django.db.models.sql import compiler
import re

# query_class returns the base class to use for Django queries.
# The custom 'SqlServerQuery' class derives from django.db.models.sql.query.Query
# which is passed in as "QueryClass" by Django itself.
#
# SqlServerQuery overrides:
# ...insert queries to add "SET IDENTITY_INSERT" if needed.
# ...select queries to emulate LIMIT/OFFSET for sliced queries.

_re_order_limit_offset = re.compile(
    r'(?:ORDER BY\s+(.+?))?\s*(?:LIMIT\s+(\d+))?\s*(?:OFFSET\s+(\d+))?$')

# Pattern to find the quoted column name at the end of a field specification
_re_pat_col = re.compile(r"\[([^[]+)\]$")

# Pattern to find each of the parts of a column name (extra_select, table, field)
_re_pat_col_parts = re.compile(
    r'(?:' +
    r'(\([^\)]+\))\s+as\s+' +
    r'|(\[[^[]+\])\.' +
    r')?' +
    r'\[([^[]+)\]$',
    re.IGNORECASE
)

# Pattern used in column aliasing to find sub-select placeholders
_re_col_placeholder = re.compile(r'\{_placeholder_(\d+)\}')

def _break(s, find):
    """Break a string s into the part before the substring to find, 
    and the part including and after the substring."""
    i = s.find(find)
    return s[:i], s[i:]

def _get_order_limit_offset(sql):
    return _re_order_limit_offset.search(sql).groups()
    
def _remove_order_limit_offset(sql):
    return _re_order_limit_offset.sub('',sql).split(None, 1)[1]


class SQLCompiler(compiler.SQLCompiler):
    def resolve_columns(self, row, fields=()):
        # If the results are sliced, the resultset will have an initial 
        # "row number" column. Remove this column before the ORM sees it.
        if self._using_row_number:
            return row[1:]
        return row

    def as_sql(self, with_limits=True, with_col_aliases=False):
        self._using_row_number = False
        
        # Get out of the way if we're not a select query or there's no limiting involved.
        check_limits = with_limits and (self.query.low_mark or self.query.high_mark is not None)
        if not check_limits:
            return super(SQLCompiler, self).as_sql(with_limits, with_col_aliases)

        raw_sql, fields = super(SQLCompiler, self).as_sql(False, with_col_aliases)
        
        # Check for high mark only and replace with "TOP"
        if self.query.high_mark is not None and not self.query.low_mark:
            _select = 'SELECT'
            if self.query.distinct:
                _select += ' DISTINCT'
            
            sql = re.sub(r'(?i)^%s' % _select, '%s TOP %s' % (_select, self.query.high_mark), raw_sql, 1)
            return sql, fields
            
        # Else we have limits; rewrite the query using ROW_NUMBER()
        self._using_row_number = True

        order, limit_ignore, offset_ignore = _get_order_limit_offset(raw_sql)
        
        qn = self.connection.ops.quote_name
        
        inner_table_name = qn('AAAA')
        fk_order_fields=[]#add pwp
        
        # Using ROW_NUMBER requires an ordering
        if order is None:
            meta = self.query.get_meta()                
            column = meta.pk.db_column or meta.pk.get_attname()
            order = '%s.%s ASC' % (inner_table_name, qn(column))
        else:
            # remap order for injected subselect
            new_order = []
            for x in order.split(','):
                if x.find('.') != -1:
                    tbl, col = x.rsplit('.', 1)
                    fk_order_fields.append(tbl+"."+col.split(' ')[0])#add pwp
                else:
                    col = x
                new_order.append('%s.%s' % (inner_table_name, col))
            order = ', '.join(new_order)
            #print 'order ------------%s,%s  \n'%(order,fk_order_fields)
        
        where_row_num = "%s < _row_num" % (self.query.low_mark)
        if self.query.high_mark:
            where_row_num += " and _row_num <= %s" % (self.query.high_mark)
            
        # Lop off ORDER... and the initial "SELECT"
        inner_select = _remove_order_limit_offset(raw_sql)
        outer_fields, inner_select = self._alias_columns(inner_select)
        
        #add pwp start
        if fk_order_fields:
            for e in fk_order_fields:
                if inner_select.find(e)==-1:
                    inner_select='%s, '%e+inner_select
        #add pwp end
        #print 'outer_fields %s \n'%outer_fields
        # map a copy of outer_fields for injected subselect
        f = []
        for x in outer_fields.split(','):
            i = x.find(' AS ')
            if i != -1:
                x = x[i+4:]
            if x.find('.') != -1:
                tbl, col = x.rsplit('.', 1)
            else:
                col = x
            f.append('%s.%s' % (inner_table_name, col.strip()))
        
        #print 'inner_select %s'%inner_select
        # inject a subselect to get around OVER requiring ORDER BY to come from FROM
        inner_select = '%s FROM ( SELECT %s ) AS %s'\
             % (', '.join(f), inner_select, inner_table_name)
        
        sql = "SELECT _row_num, %s FROM ( SELECT ROW_NUMBER() OVER ( ORDER BY %s) as _row_num, %s) as QQQ where %s"\
             % (outer_fields, order, inner_select, where_row_num)
        
        return sql, fields

    def _alias_columns(self, sql):
        """Return tuple of SELECT and FROM clauses, aliasing duplicate column names."""
        qn = self.connection.ops.quote_name
        
        outer = list()
        inner = list()
        names_seen = list()
        
        # replace all parens with placeholders
        paren_depth, paren_buf = 0, ['']
        parens, i = {}, 0
        for ch in sql:
            if ch == '(':
                i += 1
                paren_depth += 1
                paren_buf.append('')
            elif ch == ')':
                paren_depth -= 1
                key = '_placeholder_{0}'.format(i)
                buf = paren_buf.pop()
                
                # store the expanded paren string
                parens[key] = buf.format(**parens)
                paren_buf[paren_depth] += '({' + key + '})'
            else:
                paren_buf[paren_depth] += ch
    
        def _replace_sub(col):
            """Replace all placeholders with expanded values"""
            while True:
                m = _re_col_placeholder.search(col)
                if m:
                    try:
                        key = '_placeholder_{0}'.format(
                            int(m.group(1))
                        )
                        col = col.format(**{
                            key : parens[key]
                        })
                    except:
                        # not a substituted value
                        break
                else:
                    break
            return col
    
        temp_sql = ''.join(paren_buf)
    
        select_list, from_clause = _break(temp_sql, ' FROM [')
            
        for col in [x.strip() for x in select_list.split(',')]:
            match = _re_pat_col.search(col)
            if match:
                col_name = match.group(1)
                col_key = col_name.lower()

                if col_key in names_seen:
                    alias = qn('%s___%s' % (col_name, names_seen.count(col_key)))
                    outer.append(alias)
            
                    col = _replace_sub(col)
            
                    inner.append("%s as %s" % (col, alias))
                else:
                    replaced = _replace_sub(col)
                            
                    outer.append(qn(col_name))
                    inner.append(replaced)
    
                names_seen.append(col_key)
            else:
                raise Exception('Unable to find a column name when parsing SQL: {0}'.format(col))

        return ', '.join(outer), ', '.join(inner) + from_clause.format(**parens)

class SQLInsertCompiler(compiler.SQLInsertCompiler, SQLCompiler):
    def as_sql(self, *args, **kwargs):
        # Fix for Django ticket #14019
        if not hasattr(self, 'return_id'):
            self.return_id = False

        sql, params = super(SQLInsertCompiler, self).as_sql(*args, **kwargs)

        meta = self.query.get_meta()
        
        if meta.has_auto_field:
            # db_column is None if not explicitly specified by model field
            auto_field_column = meta.auto_field.db_column or meta.auto_field.column

            if auto_field_column in self.query.columns:
                quoted_table = self.connection.ops.quote_name(meta.db_table)
                sql = "SET IDENTITY_INSERT %s ON;%s;SET IDENTITY_INSERT %s OFF" %\
                    (quoted_table, sql, quoted_table)

        return sql, params


class SQLDeleteCompiler(compiler.SQLDeleteCompiler, SQLCompiler):
    pass

class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):
    pass

class SQLAggregateCompiler(compiler.SQLAggregateCompiler, SQLCompiler):
    pass

class SQLDateCompiler(compiler.SQLDateCompiler, SQLCompiler):
    pass
