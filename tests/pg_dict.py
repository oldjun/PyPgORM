from pypgorm.database import Database
from config import db
from models.user import User


if __name__ == '__main__':

    Database.connect(**db)

    # case 1
    one = User.find().where(name='jack').one(raw=True)
    print(one)

    one = User.find().where(name='jack').one()
    print(one)

    # # case 2
    # all = User.find().all()
    # print(all)
    #
    # for one in all:
    #     print(one)
