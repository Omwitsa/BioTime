from django.db.backends import BaseDatabaseIntrospection
import ado_consts

class DatabaseIntrospection(BaseDatabaseIntrospection):
    def get_table_list(self, cursor):
        "Return a list of table and view names in the current database."
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' UNION SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS")
        return [row[0] for row in cursor.fetchall()]

    def _is_auto_field(self, cursor, table_name, column_name):
        """Check if a column is an identity column.

        See: http://msdn2.microsoft.com/en-us/library/ms174968.aspx
        """
        sql = "SELECT COLUMNPROPERTY(OBJECT_ID(N'%s'), N'%s', 'IsIdentity')" % \
            (table_name, column_name)

        cursor.execute(sql)
        return cursor.fetchone()[0]

    def get_table_description(self, cursor, table_name, identity_check=True):
        """Return a description of the table, with DB-API cursor.description interface.

        The 'auto_check' parameter has been added to the function argspec.
        If set to True, the function will check each of the table's fields for the
        IDENTITY property (the IDENTITY property is the MSSQL equivalent to an AutoField).

        When a field is found with an IDENTITY property, it is given a custom field number
        of SQL_AUTOFIELD, which maps to the 'AutoField' value in the DATA_TYPES_REVERSE dict.
        """
        cursor.execute("SELECT * FROM [%s] where 1=0" % (table_name))
        columns = cursor.description

        items = list()
        for column in columns:
            column = list(column) # Convert tuple to list
            if identity_check and self._is_auto_field(cursor, table_name, column[0]):
                column[1] = ado_consts.AUTO_FIELD_MARKER
            items.append(column)
        return items

    def _name_to_index(self, cursor, table_name):
        """Return a dictionary of {field_name: field_index} for the given table.
        
        Indexes are 0-based.
        """
        return dict([(d[0], i) for i, d in enumerate(self.get_table_description(cursor, table_name, False))])

    def get_relations(self, cursor, table_name):
        source_field_dict = self._name_to_index(cursor, table_name)

        sql = """
select
    column_name = fk_cols.column_name,
    referenced_table_name = pk.table_name,
    referenced_column_name = pk_cols.column_name
from information_schema.referential_constraints ref_const
join information_schema.table_constraints fk
	on ref_const.constraint_catalog = fk.constraint_catalog
	and ref_const.constraint_schema = fk.constraint_schema
	and ref_const.constraint_name = fk.constraint_name
	and fk.constraint_type = 'foreign key'

join information_schema.table_constraints pk
	on ref_const.unique_constraint_catalog = pk.constraint_catalog
	and ref_const.unique_constraint_schema = pk.constraint_schema
	and ref_const.unique_constraint_name = pk.constraint_name
	and pk.constraint_type = 'primary key'

join information_schema.key_column_usage fk_cols
	on ref_const.constraint_name = fk_cols.constraint_name

join information_schema.key_column_usage pk_cols
	on pk.constraint_name = pk_cols.constraint_name
where
	fk.table_name = %s"""

        cursor.execute(sql,[table_name])
        relations = cursor.fetchall()
        relation_map = dict()

        for source_column, target_table, target_column in relations:
            target_field_dict = self._name_to_index(cursor, target_table)
            target_index = target_field_dict[target_column]
            source_index = source_field_dict[source_column]

            relation_map[source_index] = (target_index, target_table)

        return relation_map

    def get_indexes(self, cursor, table_name):
    #    Returns a dictionary of fieldname -> infodict for the given table,
    #    where each infodict is in the format:
    #        {'primary_key': boolean representing whether it's the primary key,
    #         'unique': boolean representing whether it's a unique index}
        sql = """
select
	C.name as [column_name],
	IX.is_unique as [unique],
    IX.is_primary_key as [primary_key]
from
	sys.tables T
	join sys.index_columns IC on IC.object_id = T.object_id
	join sys.columns C on C.object_id = T.object_id and C.column_id = IC.column_id
	join sys.indexes Ix on Ix.object_id = T.object_id and Ix.index_id = IC.index_id
where
	T.name = %s
	and (Ix.is_unique=1 or Ix.is_primary_key=1)
    -- Omit multi-column keys
	and not exists (
		select *
		from sys.index_columns cols
		where
			cols.object_id = T.object_id
			and cols.index_id = IC.index_id
			and cols.key_ordinal > 1
	)
"""
        cursor.execute(sql,[table_name])
        constraints = cursor.fetchall()
        indexes = dict()

        for column_name, unique, primary_key in constraints:
            indexes[column_name.lower()] = {"primary_key":primary_key, "unique":unique}

        return indexes


    data_types_reverse = {
        ado_consts.AUTO_FIELD_MARKER: 'AutoField',
        ado_consts.adBoolean: 'BooleanField',
        ado_consts.adChar: 'CharField',
        ado_consts.adWChar: 'CharField',
        ado_consts.adDecimal: 'DecimalField',
        ado_consts.adNumeric: 'DecimalField',
        ado_consts.adDBTimeStamp: 'DateTimeField',
        ado_consts.adDouble: 'FloatField',
        ado_consts.adSingle: 'FloatField',
        ado_consts.adInteger: 'IntegerField',
        ado_consts.adBigInt: 'IntegerField',
        #ado_consts.adBigInt: 'BigIntegerField',
        ado_consts.adSmallInt: 'IntegerField',
        ado_consts.adTinyInt: 'IntegerField',
        ado_consts.adVarChar: 'CharField',
        ado_consts.adVarWChar: 'CharField',
        ado_consts.adLongVarWChar: 'TextField',
        ado_consts.adLongVarChar: 'TextField',
    }
