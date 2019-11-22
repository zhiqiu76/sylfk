import pymysql

class DBResult(object):
    suc = False
    result = None
    error = None
    rows = None

    def index_of(self, index):
        if self.suc and isinstance(index, int) and self.rows > index >= -self.rows:
            return self.result[index]
        return None

    def get_first(self):
        return self.index_of(0)

    def get_last(self):
        return self.index_of(-1)

    @staticmethod
    def handler(func):
        def decorator(*args, **options):
            ret = DBResult()
            try:
                ret.rows, ret.result = func(*args, **options)
                ret.suc = True
            except Exception as e:
                ret.error = e
            return ret
        return decorator

    def to_dict(self):
        return {
            'suc': self.suc,
            'result': self.result,
            'error': self.error,
            'rows': self.rows,
        }

class BaseDB(object):
    def __init__(self, user, password, database='', host='127.0.0.1', port=3306, charset='utf8', cursor_class=pymysql.cursors.DictCursor):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.charset = charset
        self.cursor_class = cursor_class
        self.conn = self.connect()

    def connect(self):
        return pymysql.connect(host=self.host, user=self.user, port=self.port, passwd=self.password,
                            db=self.database, charset=self.charset, cursorclass=self.cursor_class
            )

    def close(self):
        self.conn.close()

    @DBResult.handler
    def execute(self, sql, params=None):
        with self.conn as cursor:
            rows = cursor.execute(sql, params) if params and isinstance(params, dict) else cursor.execute(sql)
            result = cursor.fetchall()
        return rows, result

    def insert(self, sql, params=None):
        ret = self.execute(sql, params)
        ret.result = self.conn.insert_id()
        return ret

    @DBResult.handler
    def process(self, func, params=None):
        with self.conn as cursor:
            rows = cursor.callproc(func, params) if params and isinstance(params, dict) else cursor.callproc(func)
            result = cursor.fetchall()
        return rows, result

    def create_db(self, db_name, db_charset='utf8'):
        return self.execute('CREATE DATABASE %s DEFAULT CHARACTER SET %s' % (db_name, db_charset))

    def drop_db(self, db_name):
        return self.execute('CREATE DATABASE %s DEFAULT CHARACTER SET %s' % (db_name, db_charset))

    @DBResult.handler
    def choose_db(self, db_name):
        self.conn.select_db(db_name)
        return None, None