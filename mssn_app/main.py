from flask import Blueprint, g, session, render_template, request, flash, redirect, current_app, g, send_from_directory, url_for
from .auth import login_required
from .models import User, Subscription, db, Executive, AcademicYear, Article, Document, DocumentCategory, Event, ArticleCategory
from sqlalchemy.exc import IntegrityError
from flask_mail import Message, Mail
from werkzeug.utils import secure_filename
import os
from flask_ckeditor import upload_success, upload_fail
from markupsafe import Markup
from flask_paginate import Pagination, get_page_parameter, get_page_args


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
    return render_template('index.html', academic_year=academic_year, events=events, articles=articles, pagination=pagination)


@bp.route('/admin/')
@login_required
def admin_dashboard():
    user = User.query.get(session['user_id'])
    subscriptions = Subscription.query.all()
    academic_year = AcademicYear.query.all()
    executive = Executive.query.all()
    document_category = DocumentCategory.query.all()
    document = Document.query.all()
    article_category = ArticleCategory.query.all()
    return render_template('dashboard.html', user=user, subscriptions=subscriptions, academic_year=academic_year, executive=executive, document_category=document_category, document=document, article_category=article_category)


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
                    'subscription_email.html', name=new_subscription.full_name)
                message = Message(subject='Welcome to MSSN OAUSTECH', sender='azeezsaheed2003@gmail.com',
                                  recipients=[new_subscription.email], html=html_content)
                mail.send(message)
                flash('You have subscribed successfully!', "success")
                return redirect(referrer)
            except IntegrityError:
                error = "Email is already registered"

        flash(error, "danger")
        return redirect(referrer)


@bp.route('/newsletter/', methods=['POST'])
def newsletter():
    referrer = request.referrer
    subject = request.form['subject']
    body = request.form['body']
    subscriptions = Subscription.query.all()
    mail = current_app.extensions['mail']

    for subscription in subscriptions:
        message = Message(subject=subject, sender='azeezsaheed2003@gmail.com',
                          body=body, recipients=[subscription.email])
        mail.send(message)

        flash('Mail has been sent successfully', "success")
        return redirect(referrer)


@bp.route('/add-academic-year', methods=['POST'])
@login_required
def add_academic_year():
    year = request.form['year']
    referrer = request.referrer
    if not year:
        flash('Year is required')
    else:
        new_academic_year = AcademicYear(year=year)
        db.session.add(new_academic_year)
        db.session.commit()
        flash('Academic year has been added successfully', "success")
    return redirect(referrer)


@bp.route('/add-executive', methods=['POST'])
@login_required
def add_executive():
    referrer = request.referrer
    academic_year_id = request.form['academic_year_id']
    name = request.form['name']
    position = request.form['position']

    if academic_year_id and name:
        new_executive = Executive(
            name=name, academic_year_id=academic_year_id, position=position)
        db.session.add(new_executive)
        db.session.commit()
        flash('Executive has been added successfully', "success")
    else:
        flash("All fields are required", "warning")

    return redirect(referrer)


@bp.route('/executive_list/')
def executive_year_list():
    academic_year = AcademicYear.query.all()
    return render_template('executive_year_list.html', academic_year=academic_year)


@bp.route('/executive_list/<path:year>')
def executive_detail_list(year):
    referrer = request.referrer
    filter_year = AcademicYear.query.filter_by(year=year).first()
    try:
        executive_list = Executive.query.filter_by(
            academic_year_id=filter_year.id)
    except:
        return redirect(referrer)
    return render_template('executive_detail_list.html', executive_list=executive_list, year=year)


@bp.route('/add-article/', methods=['POST'])
def article_create():
    referrer = request.referrer
    title = request.form['title']
    body = request.form['ckeditor']
    cover_photo = request.files['cover_photo']
    category_id = request.form['category_id']
    if cover_photo:
        filename = secure_filename(cover_photo.filename)
        # os.path.join(current_app.config['STATIC_FOLDER'], "uploads")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        document_path = os.path.join(upload_folder, filename)
        cover_photo.save(document_path)
        new_article = Article(title=title, body=body,
                              cover_photo=filename, category_id=category_id)
    else:
        new_article = Article(title=title, body=body, category_id=category_id)
    db.session.add(new_article)
    db.session.commit()
    flash('Article has been added successfully', "success")
    return redirect(referrer)


@bp.route('/add_article_category/', methods=['POST'])
def add_article_category():
    referrer = request.referrer
    category = request.form['category']
    if category:
        new_category = ArticleCategory(name=category)
        db.session.add(new_category)
        db.session.commit()
        flash("Article Category has been added", 'success')
    else:
        flash('All fields are required', 'error')
    return redirect(referrer)


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

    total = article_list.total

    pagination = Pagination(page=page, per_page=per_page,
                            total=total, record_name='articles')
    return render_template('article_list.html', article_list=article_list, pagination=pagination, categories=categories)


@bp.route('/articles/<int:id>/')
def article_detail(id):
    article = Article.query.get(id)
    return render_template('article_detail.html', article=article)


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


@bp.route('/add-document-category/', methods=['GET', 'POST'])
@login_required
def add_document_category():
    referrer = request.referrer
    name = request.form['name']
    if name:
        new_category = DocumentCategory(name=name)
        db.session.add(new_category)
        db.session.commit()
        flash("Category has been added succesfully", "success")
    else:
        flash("Category Name is required", "info")

    return redirect(referrer)


@bp.route('/add-document/', methods=['POST'])
def add_document():
    referrer = request.referrer
    title = request.form['title']
    category_id = request.form['category_id']
    document_file = request.files['document_file']
    if "user_id" in session:
        author = User.query.get(session['user_id'])

    if document_file and title and category_id:
        filename = secure_filename(document_file.filename)
        # os.path.join(current_app.config['STATIC_FOLDER'], "uploads")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        document_path = os.path.join(upload_folder, filename)
        document_file.save(document_path)
        new_book = Document(title=title, category_id=category_id,
                            document_file=filename, author_id=author.id)
        db.session.add(new_book)
        db.session.commit()
        flash('Document has been added sucessfully', "success")
    else:
        flash("All fields are required")

    return redirect(referrer)


# @bp.route('/mssn-oaustech-library/')
# def mssn_oaustech_library():
#     document_category = DocumentCategory.query.all()
#     documents = Document.query.all()
#     return render_template('library.html', documents=documents, document_category=document_category)

@bp.route('/mssn-oaustech-library/')
def mssn_oaustech_library():
    document_category = DocumentCategory.query.all()
    page = request.args.get('page', 1, type=int)
    per_page = 2  # Number of documents per page
    total = None
    for category in document_category:
        category.paginated_documents = Document.query.filter_by(category_id=category.id).paginate(page=page, per_page=per_page)
        # category.paginated_documents = category.documents.paginate(page, per_page, False)
        # category.documents = Document.query.filter_by(category_id=category.id).paginate(page, per_page, False)
        total = category.paginated_documents.total
    pagination = Pagination(page=page, per_page=per_page,
                            total=total, record_name='articles')  

    print(total) 
    return render_template('library.html', document_category=document_category,pagination=pagination)


@bp.route('/documents/<int:document_id>/download')
def download_document(document_id):
    document = Document.query.get(document_id)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, document.document_file, as_attachment=True)


@bp.route('/add-events/', methods=["POST"])
def add_event():
    referrer = request.referrer
    image = request.files['image']
    if image:
        filename = secure_filename(image.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        image_path = os.path.join(upload_folder, filename)
        image.save(image_path)
        new_event = Event(image=filename)
        db.session.add(new_event)
        db.session.commit()
        flash('Event has been added successfully', 'success')
    else:
        flash('All fields are required')

    return redirect(referrer)
