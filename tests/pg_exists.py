from pypgorm.database import Database
from config import db
from models.user import User


if __name__ == '__main__':

    Database.connect(**db)

    exists = User.find().where(name='jack').exists()
    print(exists)
