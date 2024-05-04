from flask import g, redirect, flash, url_for, request, current_app
from flask_admin import Admin, form, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField
from .models import *
from flask_mail import Message


admin = Admin(template_mode='bootstrap3')

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(AcademicYear, db.session))
admin.add_view(ModelView(Subscription, db.session))
admin.add_view(ModelView(ArticleCategory, db.session))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        # Adjust as needed based on your admin role check
        return g.user is not None and g.user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('You do not have permission to access the admin interface.', 'error')
        return redirect(url_for('auth.login', next=request.url))


class ArticleAdmin(ModelView):
    form_overrides = {
        'body': CKEditorField
    }
    create_template = 'admin/edit.html'
    edit_template = 'admin/edit.html'
    column_list = ('id', 'article_category', 'title', 'body',
                   'cover_photo', 'created_at', 'updated_at')
    form_extra_fields = {
        'cover_photo': form.ImageUploadField('Cover Photo',
                                             base_path='mssn_app/static/uploads')
    }


admin.add_view(ArticleAdmin(Article, db.session))


class DocumentCategoryAdmin(ModelView):
    form_extra_fields = {
        'cover_photo': form.ImageUploadField('Cover Photo',
                                             base_path='mssn_app/static/uploads')
    }


admin.add_view(DocumentCategoryAdmin(DocumentCategory, db.session))


class DocumentAdmin(ModelView):
    column_hide_backrefs = False
    column_list = ('id', 'category', 'title', 'document_file', 'cover_photo')
    form_extra_fields = {
        'cover_photo': form.ImageUploadField('Cover Photo',
                                             base_path='mssn_app/static/uploads'),
        'document_file': form.FileUploadField('Document File',
                                              base_path='mssn_app/static/uploads')
    }


admin.add_view(DocumentAdmin(Document, db.session))


class ExecutiveAdmin(ModelView):
    column_list = ('id', 'name', 'academic_year',
                   'position', 'department', 'timestamp')


admin.add_view(ExecutiveAdmin(Executive, db.session))


class EventAdmin(ModelView):
    form_extra_fields = {
        'image': form.ImageUploadField('Image',
                                       base_path='mssn_app/static/uploads')
    }


admin.add_view(EventAdmin(Event, db.session))


class NewsletterForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Send Newsletter')


class NewsletterAdminView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        form = NewsletterForm()
        if form.validate_on_submit():
            subject = form.subject.data
            body = form.body.data
            subscriptions = Subscription.query.all()
            mail = current_app.extensions['mail']

            for subscription in subscriptions:
                message = Message(subject=subject, sender='azeezsaheed2003@gmail.com',
                                  recipients=[subscription.email], html=body)
                mail.send(message)

            flash('Newsletter sent successfully', 'success')
            return redirect(url_for('newsletter.index'))

        return self.render('admin/newsletter.html', form=form)


admin.add_view(NewsletterAdminView(
    name='Send Newsletter', endpoint='newsletter'))
