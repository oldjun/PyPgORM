from pypgorm.database import Database
from config import db
from models.user import User


if __name__ == '__main__':

    Database.connect(**db)

    all = User.find().where('money', 'between', [150, 250]).all()
    for one in all:
        print(one)
