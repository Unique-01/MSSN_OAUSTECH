from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    documents = db.relationship('Document',backref = 'author')

    def __repr__(self):
        return self.username


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.full_name} --- {self.email}"


class AcademicYear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(), nullable=False)
    executives = db.relationship('Executive', backref='academic_year')

    def __repr__(self):
        return self.year


class Executive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey(
        'academic_year.id'), nullable=False)
    position = db.Column(db.String(), default='Test')
    department = db.Column(db.String(),nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return self.name

class ArticleCategory(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(),nullable=False)
    articles = db.relationship('Article',backref='article_category')

    def __repr__(self):
        return self.name


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    body = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cover_photo = db.Column(db.String(),nullable=True)
    category_id  = db.Column(db.Integer,db.ForeignKey('article_category.id',name='article_category_id'),nullable=True)

    def __repr__(self):
        return self.title


class DocumentCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    documents = db.relationship('Document',backref = 'document_category')

    def __repr__(self):
        return self.name

class Document(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    category_id = db.Column(db.Integer,db.ForeignKey('document_category.id'),nullable=False)
    title = db.Column(db.String(),nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_file = db.Column(db.String())

    def __repr__(self):
        return self.title

class Event(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    image = db.Column(db.String())
    
