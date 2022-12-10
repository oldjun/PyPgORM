import time
import logging
import psycopg2
import decimal
import datetime
from psycopg2 import extras
from pypgorm.batch import Batch


def escape_string(s):
    return s


class Connection(object):

    def __init__(self, host, port, user, password, database, charset='utf8', debug=False) -> None:
        self.__conn = None
        self.__debug = debug
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__database = database
        self.__charset = charset
        self.__last_ping_time = int(time.time())
        self.__ping = 3600

    def __del__(self):
        self.close()

    def open(self):
        self.close()
        try:
            config = dict(
                host=self.__host,
                port=self.__port,
                user=self.__user,
                password=self.__password,
                database=self.__database,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            if self.__debug:
                logging.info(msg=str(config))
            self.__conn = psycopg2.connect(**config)
            self.__conn.autocommit = True
            if self.__debug:
                logging.info(f'pgsql connect success')
        except Exception as e:
            if self.__debug:
                logging.error(f'pgsql connect error')
            raise e

    def close(self):
        if self.__conn is not None:
            if self.__debug:
                logging.info(f'pgsql connection closed')
            self.__conn.close()
            self.__conn = None

    def set_ping(self, seconds):
        self.__ping = seconds

    def ping(self):
        if self.__conn is None:
            return
        current_time = int(time.time())
        if current_time - self.__last_ping_time > self.__ping:
            try:
                if self.__debug:
                    logging.info('conn ping')
                sql = "select 1"
                self.__conn.fetchone(sql)
            except Exception as e:
                if self.__debug:
                    logging.error(str(e))
                self.__conn.open()
        self.__last_ping_time = int(time.time())

    def tables(self):
        sql = f"select table_name from information_schema.tables WHERE table_schema='public'"
        all = self.fetchall(sql)
        return [one['table_name'] for one in all]

    def schema(self, table):
        sql = f"select column_name,data_type from information_schema.columns where table_name='{table}' and table_schema='public';"
        all = self.fetchall(sql)
        return [dict(one) for one in all]

    def table_exists(self, table):
        sql = f"select exists(select * from information_schema.tables where table_schema='public' and table_name='{table}')"
        one = self.fetchone(sql)
        return one['exists']

    def primary_key(self, table):
        sql = f"""
        select column_name from information_schema.table_constraints
        join information_schema.key_column_usage using (table_schema, table_name)
        where table_schema='public' and table_name='{table}' and constraint_type='PRIMARY KEY'
        """
        one = self.fetchone(sql)
        return one['column_name']

    def fetchone(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            one = cursor.fetchone()
            cursor.close()
            if one is None:
                return None
            for k, v in one.items():
                if isinstance(v, datetime.datetime):
                    one[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(v, datetime.date):
                    one[k] = v.strftime('%Y-%m-%d')
                elif isinstance(v, decimal.Decimal):
                    one[k] = float(v)
            return dict(one)
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def fetchall(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            all = cursor.fetchall()
            cursor.close()
            if all is None:
                return []
            for one in all:
                for k, v in one.items():
                    if isinstance(v, datetime.datetime):
                        one[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(v, datetime.date):
                        one[k] = v.strftime('%Y-%m-%d')
                    elif isinstance(v, decimal.Decimal):
                        one[k] = float(v)
            return [dict(one) for one in all]
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def batch(self, sql):
        try:
            if self.__debug:
                logging.info(f"batch sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            return Batch(cursor)
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def insert(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            last_insert_id = cursor.lastrowid
            cursor.close()
            return last_insert_id
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def insert_batch(self, sql, data):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.executemany(sql, data)
            last_insert_id = cursor.lastrowid
            cursor.close()
            return last_insert_id
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def execute(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            num = cursor.execute(sql)
            cursor.close()
            return num
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def count(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def sum(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def min(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def max(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def average(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def exists(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchone()
            total = 0
            for v in data.values():
                total = v
            cursor.close()
            return total
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def column(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def scalar(self, sql):
        try:
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()
            return result
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def begin(self):
        try:
            sql = "begin"
            if self.__debug:
                logging.info(f"sql: {sql}")
            if self.__conn is None:
                self.open()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def rollback(self):
        try:
            sql = "rollback"
            if self.__debug:
                logging.info(f"sql: {sql}")
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def commit(self):
        try:
            sql = "commit"
            if self.__debug:
                logging.info(f"sql: {sql}")
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def savepoint(self, identifier):
        try:
            sql = f"savepoint {identifier}"
            if self.__debug:
                logging.info(f"sql: {sql}")
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def rollback_savepoint(self, identifier):
        try:
            sql = f"rollback to savepoint {identifier}"
            if self.__debug:
                logging.info(f"sql: {sql}")
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()

    def release_savepoint(self, identifier):
        try:
            sql = f"release savepoint {identifier}"
            if self.__debug:
                logging.info(f"sql: {sql}")
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
        except psycopg2.OperationalError as e:
            logging.error(str(e))
            self.open()
