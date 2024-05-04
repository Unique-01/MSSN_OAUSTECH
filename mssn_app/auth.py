from werkzeug.security import check_password_hash, generate_password_hash
from flask import request, render_template, session, flash, url_for, redirect, Blueprint, g
from .models import User, db
import functools

bp = Blueprint('auth', __name__)


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
            flash('You need to login first', "warning")
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/admin/jdfghkdjfhgkjdfh/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successfull', 'success')
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('Succesfully logged out')
    return redirect(url_for('main.index'))
