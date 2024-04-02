from flask import Blueprint,g,session,render_template,request,flash,redirect,current_app,g,send_from_directory
from .auth import login_required
from .models import User,Subscription,db,Executive,AcademicYear,Article,Document,DocumentCategory
from sqlalchemy.exc import IntegrityError
from flask_mail import Message,Mail
from werkzeug.utils import secure_filename
import os



bp = Blueprint('main',__name__)



@bp.route('/')
def index():
    academic_year = AcademicYear.query.all()

    return render_template('index.html',academic_year=academic_year)


@bp.route('/admin/')
@login_required
def admin_dashboard():
    user = User.query.get(session['user_id'])
    subscriptions = Subscription.query.all()
    academic_year = AcademicYear.query.all()
    executive = Executive.query.all()
    document_category = DocumentCategory.query.all()
    document = Document.query.all()
    return render_template('dashboard.html',user=user,subscriptions=subscriptions,academic_year=academic_year,executive=executive,document_category=document_category,document=document)

@bp.route('/subscribe',methods=['GET','POST'])
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
                new_subscription = Subscription(full_name=full_name,email=email)
                db.session.add(new_subscription)
                db.session.commit()
                html_content = render_template('subscription_email.html',name=new_subscription.full_name)
                message = Message(subject='Welcome to MSSN OAUSTECH', sender='azeezsaheed2003@gmail.com', recipients=[new_subscription.email], html=html_content)
                mail.send(message)
                flash('You have subscribed successfully!',"success")
                return redirect(referrer)
            except IntegrityError:
                error = "Email is already registered"
                
        flash(error,"danger")
        return redirect(referrer)


@bp.route('/add-academic-year',methods=['POST'])
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
        flash('Academic year has been added successfully',"success")
    return redirect(referrer)

@bp.route('/add-executive',methods=['POST'])
@login_required
def add_executive():
    referrer = request.referrer
    academic_year_id = request.form['academic_year_id']
    name = request.form['name']
    position = request.form['position']

    if academic_year_id and name:
        new_executive = Executive(name=name,academic_year_id=academic_year_id,position=position)
        db.session.add(new_executive)
        db.session.commit()
        flash('Executive has been added successfully',"success")
    else:
        flash("All fields are required","warning")
    
    return redirect(referrer)

@bp.route('/executive_list/')
def executive_year():
    academic_year = AcademicYear.query.all()
    return render_template('executive_year.html',academic_year=academic_year)



@bp.route('/executive_list/<path:year>')
def executive_list(year):
    referrer = request.referrer
    filter_year = AcademicYear.query.filter_by(year=year).first()
    try:
        executive_list = Executive.query.filter_by(academic_year_id =filter_year.id)
    except:
        return redirect(referrer)
    return render_template('executive_list.html',executive_list=executive_list)


@bp.route('/newsletter/',methods=['POST'])
def newsletter():
    referrer = request.referrer
    subject = request.form['subject']
    body = request.form['body'] 
    subscriptions = Subscription.query.all()
    mail = current_app.extensions['mail']

    for subscription in subscriptions:
        message = Message(subject=subject,sender='azeezsaheed2003@gmail.com',body=body,recipients=[subscription.email])
        mail.send(message)

        flash('Mail has been sent successfully',"success")
        return redirect(referrer)


@bp.route('/add-article/',methods=['POST'])
def article_create():
    referrer = request.referrer
    title = request.form['title']
    body = request.form['ckeditor']

    new_article = Article(title=title,body=body)
    db.session.add(new_article)
    db.session.commit()
    flash('Article has been added successfully',"success")
    return redirect(referrer)

@bp.route('/articles/')
def article_list():
    article_list = Article.query.all()
    return render_template('article_list.html',article_list=article_list)

@bp.route('/add-document-category/',methods=['GET','POST'])
@login_required
def add_document_category():
    referrer = request.referrer
    name = request.form['name']
    if name:
        new_category = DocumentCategory(name=name)
        db.session.add(new_category)
        db.session.commit()
        flash("Category has been added succesfully","success")
    else:
        flash("Category Name is required","info")

    return redirect(referrer)

        


@bp.route('/add-document/',methods=['POST'])
def add_document():
    referrer = request.referrer
    title = request.form['title']
    category_id = request.form['category_id']
    document_file = request.files['document_file']
    if "user_id" in session:
        author = User.query.get(session['user_id'])
    
    if document_file and title and category_id:
        filename = secure_filename(document_file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']  #os.path.join(current_app.config['STATIC_FOLDER'], "uploads")
        document_path = os.path.join(upload_folder,filename)
        document_file.save(document_path)
        new_book = Document(title=title,category_id=category_id,document_file=filename,author_id=author.id)
        db.session.add(new_book)
        db.session.commit()
        flash('Document has been added sucessfully',"success")
    else:
        flash("All fields are required")

    return redirect(referrer)

@bp.route('/documents/')
def document_list():
    documents = Document.query.all()
    return render_template('document_list.html',documents=documents)

@bp.route('/documents/<int:document_id>/download')
def download_document(document_id):
    document = Document.query.get(document_id)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(upload_folder,document.document_file,as_attachment=True)
    




    



    




        


        
