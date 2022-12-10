import os
from pypgorm.local import local
from pypgorm.driver.pgsql import Connection


class Database(object):

    @staticmethod
    def connect(host, port, user, password, database, charset='utf8', debug=False, lazy=True):
        conn = Connection(host=host, port=port, user=user, password=password, database=database, charset=charset, debug=debug)
        if not lazy:
            conn.open()
        local.conn = conn

    @staticmethod
    def execute(sql):
        return local.conn.execute(sql)

    @staticmethod
    def query(sql):
        return local.conn.fetchall(sql)

    @staticmethod
    def tables():
        return local.conn.tables()

    @staticmethod
    def exists(table):
        return local.conn.table_exists(table)

    @staticmethod
    def schema(table):
        return local.conn.schema(table)

    @staticmethod
    def primary_key(table):
        return local.conn.primary_key(table)

    @staticmethod
    def reflect(table, model):
        file = model.split('/')[-1]
        file = file.split('.')[0]
        cls = ''.join([word.capitalize() for word in file.split('_')])
        str = f"from pypgorm.model import Model\n\n\n"
        str += f"class {cls}(Model):\n"
        str += f"\ttablename = '{table}'\n"

        primary_key = Database.primary_key(table)
        if primary_key != 'id':
            str += f"\tprimary_key = '{primary_key}'\n"

        path = os.path.dirname(model)
        if not os.path.exists(path):
            os.makedirs(path)
        fp = open(model, 'w', encoding='utf8')
        fp.write(str)
        fp.close()
