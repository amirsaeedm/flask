# from hello import db
# # db.drop_all()
# db.create_all()

from hello import Users
u = Users()
u.password = 'cat'
print(u.password_hash)
print(u.verify_password('cat'))