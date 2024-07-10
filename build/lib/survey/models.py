from . import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean,default=False)
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin_user(self):
        return self.username == 'admin'
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True, nullable=False)
    def __repr__(self):
        return self.name

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128), index=True, nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey(Test.id), index=True, nullable=False)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_image = db.Column(db.Boolean, default=False, nullable=False)
    value = db.Column(db.String(128), index=True, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey(Question.id), index=True, nullable=False)

class TestPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), index=True, nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey(Answer.id), index=True, nullable=False)
    
