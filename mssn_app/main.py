from flask import Blueprint, render_template,request, flash, redirect, current_app, send_from_directory, url_for
from .models import User, Subscription, db, Executive, AcademicYear, Article, Document, DocumentCategory, Event, ArticleCategory
from sqlalchemy.exc import IntegrityError
from flask_mail import Message, Mail
import os
from flask_ckeditor import upload_success, upload_fail
from markupsafe import Markup
from flask_paginate import Pagination, get_page_parameter
from decouple import config


bp = Blueprint('main', __name__)


def strip_html_tags(text):
    """Remove HTML tags from the given text."""
    return Markup(text).striptags()


@bp.route('/')
def index():
    academic_year = AcademicYear.query.all()
    events = Event.query.all()
    # Articles objects with pagination
    per_page = 6
    page = request.args.get(get_page_parameter(), type=int, default=1)
    articles = Article.query.order_by(
        Article.updated_at.desc()).paginate(page=page, per_page=per_page)
    total = len(Article.query.all())
    pagination = Pagination(page=page, per_page=per_page,
                            total=total, record_name='articles')
    return render_template('main/index.html', academic_year=academic_year, events=events, articles=articles, pagination=pagination)


@bp.route('/subscribe', methods=['GET', 'POST'])
def subscription():
    if request.method == 'POST':
        error = None
        referrer = request.referrer
        email = request.form['email']
        full_name = request.form['full_name']
        mail = current_app.extensions['mail']

        if not email and full_name:
            error = "All fields are required"
        if error is None:
            try:
                new_subscription = Subscription(
                    full_name=full_name, email=email)
                db.session.add(new_subscription)
                db.session.commit()
                html_content = render_template(
                    'main/subscription_email.html', name=new_subscription.full_name)
                message = Message(subject='Welcome to MSSN OAUSTECH', sender=config('MAIL_USERNAME'),
                                  recipients=[new_subscription.email], html=html_content)
                mail.send(message)
                flash('You have subscribed successfully!', "success")
                return redirect(referrer)
            except IntegrityError:
                error = "Email is already registered"

        flash(error, "danger")
        return redirect(referrer)


@bp.route('/executive_list/')
def executive_year_list():
    academic_year = AcademicYear.query.all()
    return render_template('main/executive_year_list.html', academic_year=academic_year)


@bp.route('/executive_list/<path:year>')
def executive_detail_list(year):
    referrer = request.referrer
    filter_year = AcademicYear.query.filter_by(year=year).first()
    try:
        executive_list = Executive.query.filter_by(
            academic_year_id=filter_year.id)
    except:
        return redirect(referrer)
    return render_template('main/executive_detail_list.html', executive_list=executive_list, year=year)


@bp.route('/articles/')
def article_list():
    category_id = request.args.get('category')
    search_query = request.args.get('q')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 6
    categories = ArticleCategory.query.all()
    if search_query:
        article_list = Article.query.filter(Article.title.ilike(f"%{search_query}%")).order_by(
            Article.updated_at.desc()).paginate(page=page, per_page=per_page)
    else:
        if category_id:
            article_list = Article.query.filter_by(category_id=category_id).order_by(
                Article.updated_at.desc()).paginate(page=page, per_page=per_page)
        else:
            article_list = Article.query.order_by(
                Article.updated_at.desc()).paginate(page=page, per_page=per_page)

    # If no results found for the search query
    if article_list.total == 0:
        message = f"No results found for '{search_query}'."
        return render_template('main/no_results.html', message=message)

    total = article_list.total

    pagination = Pagination(page=page, per_page=per_page,
                            total=total, record_name='articles')
    return render_template('main/article_list.html', article_list=article_list, pagination=pagination, categories=categories)


@bp.route('/articles/<int:id>/')
def article_detail(id):
    article = Article.query.get(id)
    latest_posts = Article.query.filter(Article.id != id).order_by(
        Article.updated_at.desc()).limit(4).all()
    return render_template('main/article_detail.html', article=article, latest_posts=latest_posts)


@bp.route('/mssn-oaustech-library/')
def mssn_oaustech_library():
    document_category = DocumentCategory.query.all()
    for category in document_category:
        category.documents = Document.query.filter_by(
            category_id=category.id).all()
    return render_template('main/library.html', document_category=document_category)


@bp.route('/documents/<int:document_id>/download')
def download_document(document_id):
    document = Document.query.get(document_id)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, document.document_file, as_attachment=True)


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    f = request.files.get('upload')
    if f:
        extension = f.filename.split('.')[-1].lower()
        if extension not in ['jpg', 'gif', 'png', 'jpeg']:
            return upload_fail(message='Image only!')
        f.save(os.path.join(upload_folder, f.filename))
        url = url_for('main.uploaded_files', filename=f.filename)
        return upload_success(url, filename=f.filename)
    return upload_fail(message='No file uploaded')


# Route for serving uploaded files
@bp.route('/files/<path:filename>')
def uploaded_files(filename):
    path = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(path, filename)


@bp.route('/contact-us')
def contact_us():
    return render_template('main/contact.html')

@bp.route('/donate')
def donate():
    return render_template('main/donate.html')