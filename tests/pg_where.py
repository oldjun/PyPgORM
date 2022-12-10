from pypgorm.database import Database
from config import db
from models.user import User


if __name__ == '__main__':

    Database.connect(**db)

    name = 'jack'
    gender = 1
    all = User.find().where("name='%s' and gender=%s" % (name, gender)).all()
    for one in all:
        print(one)
