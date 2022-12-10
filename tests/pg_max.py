from pypgorm.database import Database
from config import db
from models.user import User


if __name__ == '__main__':

    Database.connect(**db)

    money = User.find().where(status=0).max('money')
    print(money)