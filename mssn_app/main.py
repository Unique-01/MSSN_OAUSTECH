from flask import Blueprint,g,session,render_template,request,flash,redirect
from .auth import login_required
from .models import User,Subscription,db
from sqlalchemy.exc import IntegrityError



bp = Blueprint('main',__name__)

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    subscriptions = Subscription.query.all()
    return render_template('dashboard.html',user=user,subscriptions=subscriptions)

@bp.route('/subscribe',methods=['GET','POST'])
def subscription():
    if request.method == 'POST':
        error = None
        referrer = request.referrer
        email = request.form['email']
        full_name = request.form['full_name']

        if not email and full_name:
            error = "All fields are required"
        if error is None:
            try:
                new_subscription = Subscription(full_name=full_name,email=email)
                db.session.add(new_subscription)
                db.session.commit()
                flash('You have subscribed successfully!')
                return redirect(referrer)
            except IntegrityError:
                error = "Email is already registered"
                
        flash(error)
        return redirect(referrer)
        


        
