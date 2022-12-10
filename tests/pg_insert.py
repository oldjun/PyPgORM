from pypgorm.database import Database
from config import db
from models.user import User


if __name__ == '__main__':

    Database.connect(**db, lazy=False)

    User.truncate()

    user = User()
    user.name = 'jack'
    user.phone = '18976641111'
    user.money = 100
    user.gender = 1
    user.save()
