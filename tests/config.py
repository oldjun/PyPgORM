import logging

db = dict(
    host='127.0.0.1',
    port=5432,
    user='postgres',
    password='password',
    database='postgres',
    debug=True
)

logging.basicConfig(level=logging.DEBUG)
