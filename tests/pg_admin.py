from pypgorm.database import Database
from config import db
from models.admin import Admin
from models.admin_role import AdminRole
from models.admin_auth import AdminAuth


if __name__ == '__main__':

    Database.connect(**db)

    Admin.truncate()
    AdminRole.truncate()
    AdminAuth.truncate()

    for name in ['role1', 'role2', 'role3']:
        exists = AdminRole.find().where(name=name).exists()
        if not exists:
            AdminRole(name=name).save()

    admin_list = [
        dict(username='jack', phone='18976641111', money=100, role=1),
        dict(username='lucy', phone='18976642222', money=200, role=1),
        dict(username='lily', phone='18976643333', money=300, role=2)
    ]
    for item in admin_list:
        model = Admin()
        model.username = item['username']
        model.phone = item['phone']
        model.money = item['money']
        model.role = item['role']
        model.save()

    admin_auth_list = [
        dict(role=1, action='eat'),
        dict(role=2, action='play')
    ]
    for item in admin_auth_list:
        model = AdminAuth()
        model.role = item['role']
        model.action = item['action']
        model.save()
