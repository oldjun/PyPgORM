from pypgorm.database import Database
from config import db
from models.admin import Admin
from models.admin_role import AdminRole
from models.admin_auth import AdminAuth


if __name__ == '__main__':

    Database.connect(**db)

    # # case 1
    # all = Admin.find().select('a.*').alias('a') \
    #     .join(table=AdminRole.tablename, alias='r', on='a.role = r.id') \
    #     .where('r.name', '=', 'role1') \
    #     .all()
    # for one in all:
    #     print(one)

    # # case 2
    # all = Admin.find().alias('a') \
    #     .join(table=AdminRole.tablename, alias='r', on='a.role=r.id', type='left')\
    #     .where('a.lock', '=', 0) \
    #     .all()
    # for one in all:
    #     print(one)

    # # case 3
    # all = Admin.find().select('a.*').alias('a') \
    #     .join(table=AdminRole.tablename, alias='r', on='a.role=r.id', type='left')\
    #     .where('a.lock', '=', 0) \
    #     .all()
    # for one in all:
    #     print(one)

    # case 4
    all = Admin.find().select('username', 'a.role').alias('a') \
        .join(table=AdminRole.tablename, alias='r', on='a.role=r.id') \
        .join(table=AdminAuth.tablename, alias='t', on='t.role=r.id') \
        .where('t.action', '=', 'play') \
        .all()
    for one in all:
        print(one)
