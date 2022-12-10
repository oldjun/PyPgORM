from pypgorm.connection_pool import ConnectionPool
from config import db

if __name__ == '__main__':
    pool = ConnectionPool()
    pool.size(size=3)
    pool.ping(seconds=1)
    pool.create(**db, lazy=False)

    conn = pool.get()
