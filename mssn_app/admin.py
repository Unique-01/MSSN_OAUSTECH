from flask import g, redirect, flash, url_for, request, current_app
from flask_admin import Admin, form, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField
from .models import *
from flask_mail import Message
from decouple import config


admin = Admin(template_mode='bootstrap3')

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(AcademicYear, db.session))
admin.add_view(ModelView(Subscription, db.session))
admin.add_view(ModelView(ArticleCategory, db.session))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        about_section = AboutSection.query.first()
        about_page = AboutPage.query.first()
        if not about_section:
            about_section = AboutSection(content="Default Text")
            db.session.add(about_section)
            db.session.commit()
        if not about_page:
            about_page = AboutPage(content="Default Text")
            db.session.add(about_page)
            db.session.commit()
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
                                             base_path=config('UPLOAD_FOLDER'))
    }


admin.add_view(ArticleAdmin(Article, db.session))


class DocumentCategoryAdmin(ModelView):
    form_extra_fields = {
        'cover_photo': form.ImageUploadField('Cover Photo',
                                             base_path=config('UPLOAD_FOLDER'))
    }


admin.add_view(DocumentCategoryAdmin(DocumentCategory, db.session))


class DocumentAdmin(ModelView):
    column_hide_backrefs = False
    column_list = ('id', 'category', 'title', 'document_file', 'cover_photo')
    form_extra_fields = {
        'cover_photo': form.ImageUploadField('Cover Photo',
                                             base_path=config('UPLOAD_FOLDER')),
        'document_file': form.FileUploadField('Document File',
                                              base_path=config('UPLOAD_FOLDER'))
    }


admin.add_view(DocumentAdmin(Document, db.session))


class ExecutiveAdmin(ModelView):
    column_list = ('id', 'name', 'academic_year',
                   'position', 'department', 'timestamp')


admin.add_view(ExecutiveAdmin(Executive, db.session))


class EventAdmin(ModelView):
    form_extra_fields = {
        'image': form.ImageUploadField('Image',
                                       base_path=config('UPLOAD_FOLDER'))
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


class AboutSectionForm(FlaskForm):
    content = TextAreaField("About Section Content",
                            validators=[DataRequired()])
    submit = SubmitField("Update")


class AboutSectionAdminView(ModelView):
    can_create = False
    can_delete = False


admin.add_view(AboutSectionAdminView(AboutSection, db.session))


class AboutPageAdminView(ModelView):
    can_create = False
    can_delete = False
    form_overrides = {
        'content': CKEditorField
    }
    edit_template = 'admin/about_edit.html'


admin.add_view(AboutPageAdminView(AboutPage, db.session))
