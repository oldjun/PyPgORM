from pypgorm.database import Database
from config import db
from models.user import User


if __name__ == '__main__':

    Database.connect(**db)

    batch = User.find().batch(size=2, raw=True)
    for all in batch:
        print('-' * 20)
        for one in all:
            print(one)
