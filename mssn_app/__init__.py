from flask import Flask
from decouple import config
import os
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_admin import Admin
from werkzeug.security import generate_password_hash
from .models import User, db

ckeditor = CKEditor()


def create_admin_user(app):
    # Check if the admin user already exists
    admin_username = config('ADMIN_USERNAME')
    admin_password = config('ADMIN_PASSWORD')
    admin_email = config('ADMIN_EMAIL')
    admin_user = User.query.filter_by(username=admin_username).first()

    if not admin_user:
        # Create the admin user with predefined credentials
        hashed_password = generate_password_hash(admin_password)
        admin_user = User(username=admin_username, email=admin_email,
                          password=hashed_password, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
        print('Admin user created successfully.')


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SECRET_KEY'] = config('SECRET_KEY')
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = config('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = config('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, "uploads")
    app.config['CKEDITOR_FILE_UPLOADER'] = 'main.upload'
    app.config['CKEDITOR_PKG_TYPE'] = 'full'
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    from .models import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)
    ckeditor.init_app(app)

    from . import auth
    from . import main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)

    mail = Mail(app)

    from .main import strip_html_tags
    app.jinja_env.filters['strip_html_tags'] = strip_html_tags

    from .admin import admin, MyAdminIndexView
    admin.init_app(app, index_view=MyAdminIndexView())

    # Create the admin user during app initialization
    with app.app_context():
        create_admin_user(app)

    return app
