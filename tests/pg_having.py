from pypgorm.database import Database
from config import db
from models.user import User

if __name__ == '__main__':
    Database.connect(**db)

    all = User.find() \
        .select('gender', 'count(*) as count', 'avg(money) as avg', 'sum(money) as total') \
        .group('gender') \
        .having('sum(money)', '>', 200) \
        .all()
    for one in all:
        print(one)
