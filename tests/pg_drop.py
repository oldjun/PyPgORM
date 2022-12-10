from pypgorm.database import Database
from config import db


if __name__ == '__main__':

    Database.connect(**db)

    Database.execute('drop table t_user')
    Database.execute('drop table t_admin')
    Database.execute('drop table t_admin_role')
    Database.execute('drop table t_admin_auth')
