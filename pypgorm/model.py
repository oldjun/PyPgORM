from pypgorm.driver.pgsql import escape_string
from pypgorm.local import local
import pprint


class Model(object):
    tablename = None
    primary_key = 'id'

    def __init__(self, **kwargs) -> None:
        self.__conn = local.conn
        self.__sql = ''
        self.__old_fields = {}
        self.__new_fields = {}
        self.__select = []
        self.__update = {}
        self.__where = []
        self.__order = ''
        self.__group = ''
        self.__having = ''
        self.__offset = ''
        self.__limit = ''
        self.__alias = ''
        self.__join = []
        self.__quote = '"'
        for field, value in kwargs.items():
            self.__new_fields[field] = value

    def __del__(self):
        pass

    def __setattr__(self, name, value):
        if name.find('_Model__') >= 0:
            self.__dict__[name] = value
        else:
            if value is not None:
                if isinstance(value, str):
                    self.__dict__['_Model__new_fields'][name] = escape_string(value)
                else:
                    self.__dict__['_Model__new_fields'][name] = value

    def __getattr__(self, name):
        if name in self.__new_fields:
            value = self.__new_fields[name]
        elif name in self.__old_fields:
            value = self.__old_fields[name]
        else:
            raise Exception(f"object has no attribute '{name}'")
        return value

    def __setitem__(self, key, value):
        self.__dict__['_Model__new_fields'][key] = value

    def __getitem__(self, item):
        return getattr(self, item)

    def keys(self):
        fields = {}
        fields.update(self.__old_fields)
        fields.update(self.__new_fields)
        return fields.keys()

    def __str__(self):
        fields = {}
        fields.update(self.__old_fields)
        fields.update(self.__new_fields)
        return str(fields)

    def print(self):
        fields = {}
        fields.update(self.__old_fields)
        fields.update(self.__new_fields)
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(fields)

    @classmethod
    def find(cls):
        return cls()

    @classmethod
    def insert(cls, fields, values):
        model = cls()
        cols = ','.join([f"{model.__quote}{field}{model.__quote}" for field in fields])
        rows = ','.join([f"%s" for _ in range(len(fields))])
        sql = f"insert into {model.__quote}{model.__class__.tablename}{model.__quote}({cols}) values({rows})"
        return model.__conn.insert_batch(sql.strip(), values)

    @classmethod
    def truncate(cls):
        model = cls()
        if model.__class__.tablename is None:
            raise Exception('missing table name')
        sql = f'truncate table {model.__quote}{model.__class__.tablename}{model.__quote}'
        return model.__conn.execute(sql.strip())

    @classmethod
    def schema(cls):
        model = cls()
        table = model.tablename
        return model.__conn.schema(table)

    def save(self):
        if self.__old_fields.get(self.__class__.primary_key) is None:
            fields = ','.join([f"{self.__quote}{item}{self.__quote}" for item in self.__new_fields.keys()])
            values = ','.join([f"'{item}'" for item in self.__new_fields.values()])
            if len(fields) == 0:
                raise Exception('insert fields is empty')
            sql = f"insert into {self.__quote}{self.__class__.tablename}{self.__quote}({fields}) values({values})"
            self.__sql = sql
            last_insert_id = self.__conn.insert(sql)
            if self.__class__.primary_key not in self.__new_fields:
                self.__new_fields[self.__class__.primary_key] = last_insert_id
        else:
            update_str = ','.join([f"{self.__quote}{k}{self.__quote}='{v}'" for (k, v) in self.__new_fields.items()])
            if update_str != '':
                sql = f"update {self.__quote}{self.__class__.tablename}{self.__quote} set {update_str} where {self.__quote}{self.__class__.primary_key}{self.__quote}='{self.__old_fields.get(self.__class__.primary_key)}'"
                self.__sql = sql
                self.__conn.execute(sql)

    def sql(self):
        sql = self.__build_select_sql()
        if self.__alias:
            sql += f"as {self.__quote}{self.__alias}{self.__quote} "
        sql += self.__build_join_sql()
        sql += self.__build_where_sql()
        sql += self.__build_other_sql()
        self.__sql = sql.strip()
        return self.__sql

    def __build_select_sql(self):
        sql = f"select "
        if len(self.__select) > 0:
            if self.__alias:
                pk = f"{self.__quote}{self.__alias}{self.__quote}.{self.__quote}{self.primary_key}{self.__quote}"
                if pk not in self.__select:
                    ak = f"{self.__quote}{self.__alias}{self.__quote}.*"
                    if ak not in self.__select:
                        if not self.__group:
                            self.__select.insert(0, pk)
            else:
                pk = f"{self.__quote}{self.primary_key}{self.__quote}"
                if pk not in self.__select:
                    if '*' not in self.__select:
                        if not self.__group:
                            self.__select.insert(0, pk)
            sql += ','.join([f"{item}" for item in self.__select])
        else:
            sql += "*"
        sql += f" from {self.__quote}{self.__class__.tablename}{self.__quote} "
        return sql

    def __build_where_sql(self):
        sql = ''
        cond_list = []
        for cond in self.__where:
            if cond['op'] in ['=', '!=', '>', '>=', '<', '<=', 'like', 'not like']:
                value = cond['value']
                if isinstance(value, str):
                    value = escape_string(value)
                cond_list.append(f"{cond['field']} {cond['op']} '{value}'")
            elif cond['op'] in ['in', 'not in']:
                if not isinstance(cond['value'], list):
                    raise Exception('condition in or not in should be a list')
                v_list = []
                for v in cond['value']:
                    if isinstance(v, str):
                        v = escape_string(v)
                    v_list.append(f"'{v}'")
                cond_list.append(f"{cond['field']} {cond['op']} ({','.join(v_list)})")
            elif cond['op'] in ['is', 'is not']:
                if cond['value'] is not None:
                    raise Exception(f"syntax error: value should be None")
                cond_list.append(f"{cond['field']} {cond['op']} null")
            elif cond['op'] == 'between':
                if not isinstance(cond['value'], list):
                    raise Exception('condition in or not in should be a list')
                if len(cond['value']) != 2:
                    raise Exception('condition should have two element')
                cond_list.append(f"{cond['field']} between '{cond['value'][0]}' and '{cond['value'][1]}'")
            elif cond['op'] == '':
                if len(self.__where) > 1:
                    cond_list.append(f"({cond['value']})")
                else:
                    cond_list.append(f"{cond['value']}")
            else:
                raise Exception(f"syntax error: operator not supported {cond['op']}")
        where_sql = ' and '.join(cond_list)
        if where_sql:
            sql = f"where {where_sql} "
        return sql

    def __build_other_sql(self):
        sql = ''
        if self.__group:
            sql += f"group by {self.__group} "
        if self.__having:
            sql += f"having {self.__having} "
        if self.__order:
            sql += f"order by {self.__order} "
        if self.__limit:
            if self.__offset:
                sql += f"limit {self.__limit} offset {self.__offset}"
            else:
                sql += f"limit {self.__limit}"
        return sql

    def __build_join_sql(self):
        sql = ''
        for join in self.__join:
            arr = join['on'].split('=')
            if len(arr) != 2:
                raise Exception(f"syntax error: join on condition {join['on']}")
            field_arr = []
            for field in [one.strip() for one in arr]:
                _arr = field.split('.')
                if len(_arr) != 2:
                    raise Exception(f"syntax error: join on condition {join['on']}")
                field_str = f"{self.__quote}{_arr[0].strip()}{self.__quote}.{self.__quote}{_arr[1].strip()}{self.__quote}"
                field_arr.append(field_str)
            on = '='.join(field_arr)
            sql += f"{join['type']} join {self.__quote}{join['table']}{self.__quote} as {self.__quote}{join['alias']}{self.__quote} on {on} "
        return sql

    def one(self, raw=False):
        if self.__class__.tablename is None:
            raise Exception('missing table name')

        self.__limit = 1
        sql = self.sql()

        one = self.__conn.fetchone(sql)
        if one is None:
            return None

        if raw:
            return one

        res = self.__class__()
        for (k, v) in one.items():
            res.__old_fields[k] = v
        return res

    def all(self, raw=False):
        if self.__class__.tablename is None:
            raise Exception('missing table name')
        sql = self.sql()
        all = self.__conn.fetchall(sql)
        if raw:
            return all

        res = []
        for one in all:
            item = self.__class__()
            for (k, v) in one.items():
                item.__old_fields[k] = v
            res.append(item)
        return res

    def alias(self, alias):
        self.__alias = alias
        return self

    def join(self, table, alias, on, type='inner'):
        self.__join.append(dict(table=table, alias=alias, on=on, type=type))
        return self

    def select(self, *args):
        arg_list = []
        for arg in args:
            arg = arg.strip()
            arr = arg.split()
            field = ''
            if len(arr) > 1:
                if len(arr) == 2:
                    pass
                if len(arr) == 3:
                    if arr[1].lower() != 'as':
                        raise Exception(f'select statement error: {arg}')
                    del arr[1]
                field = f"{arr[0]} as {self.__quote}{arr[1]}{self.__quote}"
            else:
                if arg.find('.'):
                    temp = []
                    for v in arg.split('.'):
                        if v == '*':
                            temp.append(v)
                        else:
                            temp.append(f"{self.__quote}{v}{self.__quote}")
                    field = '.'.join(temp)
                else:
                    if arg == '*':
                        field = arg
                    else:
                        field = f"{self.__quote}{arg}{self.__quote}"
            if field != '':
                arg_list.append(field)
        self.__select.extend(arg_list)
        return self

    def update(self, **kwargs):
        if self.__class__.tablename is None:
            raise Exception('missing table name')
        self.__update.update(kwargs)
        sql = f"update {self.__quote}{self.__class__.tablename}{self.__quote} "
        update_str = ','.join([f"{self.__quote}{k}{self.__quote}='{v}'" for (k, v) in self.__update.items()])
        if not update_str:
            raise Exception('missing update statement')
        sql += f"set {update_str} "
        sql += self.__build_where_sql()
        sql += self.__build_other_sql()
        self.__sql = sql.strip()
        return self.__conn.execute(self.__sql)

    def delete(self):
        if self.__class__.tablename is None:
            raise Exception('missing table name')

        sql = f"delete from {self.__quote}{self.__class__.tablename}{self.__quote} "
        if self.__old_fields.get(self.__class__.primary_key) is None:
            sql += self.__build_where_sql()
            sql += self.__build_other_sql()
        else:
            sql += f"where {self.__quote}{self.__class__.primary_key}{self.__quote}='{self.__old_fields.get(self.__class__.primary_key)}'"

        self.__sql = sql.strip()
        return self.__conn.execute(self.__sql)

    def where(self, *args, **kwargs):
        if len(args) > 0:
            if len(args) == 1:
                cond = dict()
                cond['op'] = ''
                cond['field'] = ''
                cond['value'] = args[0]
                self.__where.append(cond)
            elif len(args) == 3:
                field = args[0]
                value = args[2]
                if field.find('.'):
                    field = '.'.join([f"{self.__quote}{v}{self.__quote}" for v in field.split('.')])
                op = args[1].lower()
                op = ' '.join([o for o in op.split()])
                cond = dict()
                cond['op'] = op
                cond['field'] = field
                cond['value'] = value
                self.__where.append(cond)
            else:
                raise Exception('where statement error')
        if len(kwargs) > 0:
            for k, v in kwargs.items():
                cond = dict()
                cond['op'] = '='
                cond['field'] = f"{self.__quote}{k}{self.__quote}"
                cond['value'] = v
                self.__where.append(cond)
        return self

    def order(self, order):
        self.__order = order
        return self

    def group(self, group):
        self.__group = f"{group}"
        return self

    def having(self, *args):
        if len(args) != 3:
            raise Exception(f'having statement error')
        self.__having = f"{args[0]} {args[1]} {args[2]}"
        return self

    def offset(self, offset):
        self.__offset = offset
        return self

    def limit(self, limit):
        self.__limit = limit
        return self

    def count(self, field=None):
        if self.__class__.tablename is None:
            raise Exception('missing table name')
        sql = "select "
        if field is not None:
            if field.find('.'):
                temp = []
                for v in field.split('.'):
                    if v == '*':
                        temp.append(v)
                    else:
                        temp.append(f"{self.__quote}{v}{self.__quote}")
                field = '.'.join(temp)
            else:
                if field != '*':
                    field = f"{self.__quote}{field}{self.__quote}"
            sql += f"count({field}) "
        else:
            sql += f"count(*) "
        sql += f"from {self.__quote}{self.__class__.tablename}{self.__quote} "
        if self.__alias:
            sql += f"as {self.__quote}{self.__alias}{self.__quote} "
        sql += self.__build_join_sql()
        sql += self.__build_where_sql()
        sql += self.__build_other_sql()
        if self.__group:
            self.__sql = f"select count(*) from ({sql.strip()}) as {self.__quote}t{self.__quote}"
        else:
            self.__sql = sql.strip()
        return self.__conn.count(self.__sql)

    def __build_simple_sql(self, field, func=''):
        if self.__class__.tablename is None:
            raise Exception('missing table name')

        if field is None:
            raise Exception('field is None')

        sql = "select "
        if field.find('.'):
            temp = []
            for v in field.split('.'):
                temp.append(f"{self.__quote}{v}{self.__quote}")
            field = '.'.join(temp)
        else:
            field = f"{self.__quote}{field}{self.__quote}"
        if func:
            sql += f"{func}({field}) "
        else:
            sql += f"{field} "
        sql += f"from {self.__quote}{self.__class__.tablename}{self.__quote} "
        if self.__alias:
            sql += f"as {self.__quote}{self.__alias}{self.__quote} "
        sql += self.__build_join_sql()
        sql += self.__build_where_sql()
        sql += self.__build_other_sql()
        return sql.strip()

    def sum(self, field):
        self.__sql = self.__build_simple_sql(field, 'sum')
        return self.__conn.sum(self.__sql)

    def min(self, field):
        self.__sql = self.__build_simple_sql(field, 'min')
        return self.__conn.min(self.__sql)

    def max(self, field):
        self.__sql = self.__build_simple_sql(field, 'max')
        return self.__conn.max(self.__sql)

    def average(self, field):
        self.__sql = self.__build_simple_sql(field, 'avg')
        return self.__conn.average(self.__sql)

    def exists(self):
        if self.__class__.tablename is None:
            raise Exception('missing table name')
        sql = f"select exists({self.sql()})"
        self.__sql = sql.strip()
        return self.__conn.exists(sql)

    def column(self, field):
        self.__sql = self.__build_simple_sql(field)
        result = self.__conn.column(self.__sql)
        res = []
        for item in result:
            for _, v in item.items():
                res.append(v)
        return res

    def scalar(self, field):
        self.__limit = 1
        self.__sql = self.__build_simple_sql(field)
        result = self.__conn.scalar(self.__sql)
        if result is None:
            return None
        for _, v in result.items():
            return v

    def batch(self, size=100, raw=False):
        if self.__class__.tablename is None:
            raise Exception('missing table name')
        total = self.count()
        sql = self.sql()
        batch = self.__conn.batch(sql)
        batch.raw(raw=raw)
        batch.size(size=size)
        batch.total(total=total)
        batch.model(self)
        return batch
