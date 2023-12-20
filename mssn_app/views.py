
from werkzeug.security import check_password_hash,generate_password_hash
from flask import request,render_template,session,flash,url_for,redirect,Blueprint
from .models import User,db

bp = Blueprint('views',__name__)

@bp.route('/register',methods=['GET','POST'])
def register():
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        new_user = User(username=username,email=email,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        flash("Registration successfull, You're now logged in",'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@bp.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username = username).first()
        if user and check_password_hash(user.password,password):
            session['user_id'] = user.id
            flash('Login successfull','success')
            return redirect(url_for('views.dashboard'))
        else:
            flash('Invalid credentials','error')

    return render_template('login.html')

@bp.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    else:
        flash('You need to login first')
        return redirect('login')
    return render_template('dashboard.html',user=user)


