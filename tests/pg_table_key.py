from pypgorm.database import Database
from config import db


if __name__ == '__main__':
    Database.connect(**db)

    table = 't_user'
    pk = Database.primary_key(table)
    print(pk)
