from werkzeug.security import check_password_hash,generate_password_hash
from flask import request,render_template,session,flash,url_for,redirect,Blueprint,g
from .models import User,db
import functools

bp = Blueprint('auth',__name__)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('You need to login first')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


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
        return redirect(url_for('main.dashboard'))

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
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials','error')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Succesfully logged out')
    return redirect(url_for('home'))




