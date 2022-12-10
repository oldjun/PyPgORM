from pypgorm.database import Database
from tests.config import db
from tests.models.user import User


if __name__ == '__main__':

    Database.connect(**db)

    money = User.find().where(name='jack').scalar('money')
    print(money)
