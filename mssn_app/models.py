from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(30),unique=True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    password = db.Column(db.String(),nullable=False)
    date_joined = db.Column(db.DateTime,default= datetime.utcnow)


    def __repr__(self):
        return self.username