from pypgorm.database import Database
from config import db


if __name__ == '__main__':

    Database.connect(**db)

    fp = open('pgsql/t_user.sql', 'r', encoding='utf-8')
    sql = fp.read()
    Database.execute(sql)
    fp.close()

