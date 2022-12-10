from pypgorm.database import Database
from config import db
from models.user import User


if __name__ == '__main__':

    Database.connect(**db)

    # case 1
    one = User.find().where(name='jack').one()
    one.gender = 1
    one.save()

    # # case 2
    # User.find().where(name='jack').update(money=180, gender=0)
