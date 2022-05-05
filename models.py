
#\c User
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class Users(db.Model):
    __tablename__ = 'users'

    def __repr__(self):
        u = self
        return f"<User username={u.username} password={u.password} email={u.email} first_name={u.first_name} last_name={u.last_name}>"

    username = db.Column(db.String(20), primary_key=True, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    feedback = relationship("Feedbacks", cascade="all, delete", passive_deletes=True)

class Feedbacks(db.Model):
    __tablename__ = 'feedback'

    def __repr__(self):
        f = self
        return f"<Feedback id={f.id} title={f.title} content={f.content} username={f.username}"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Text, nullable=False)
    posted_to = db.Column(db.ForeignKey('users.username', ondelete="cascade"))
