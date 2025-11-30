"""
Flask-WTF Forms
Form validation and CSRF protection
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError

from models import User, Category, Department


class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username/Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    """User registration form"""
    user_id = StringField('User ID', validators=[
        DataRequired(),
        Length(min=5, max=50)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    phone = StringField('Phone', validators=[
        Optional(),
        Length(max=20)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[
        ('student', 'Student'),
        ('faculty', 'Faculty')
    ], validators=[DataRequired()])
    department = SelectField('Department', coerce=str, validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Populate department choices
        departments = Department.query.filter_by(is_active=True).all()
        self.department.choices = [('', 'Select Department')] + [
            (dept.code, dept.name) for dept in departments
        ]
    
    def validate_user_id(self, field):
        if User.query.filter_by(user_id=field.data.upper()).first():
            raise ValidationError('User ID already registered.')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class PasswordResetRequestForm(FlaskForm):
    """Password reset request form"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])


class PasswordResetForm(FlaskForm):
    """Password reset form"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])


class BookForm(FlaskForm):
    """Book add/edit form"""
    isbn = StringField('ISBN', validators=[DataRequired(), Length(max=20)])
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    author = StringField('Author', validators=[DataRequired(), Length(max=100)])
    publisher = StringField('Publisher', validators=[Optional(), Length(max=100)])
    publication_year = IntegerField('Publication Year', validators=[Optional()])
    edition = StringField('Edition', validators=[Optional(), Length(max=20)])
    category = SelectField('Category', coerce=str, validators=[Optional()])
    department = SelectField('Department', coerce=str, validators=[Optional()])
    language = StringField('Language', validators=[Optional(), Length(max=30)])
    pages = IntegerField('Pages', validators=[Optional()])
    total_copies = IntegerField('Total Copies', validators=[DataRequired()])
    shelf_location = StringField('Shelf Location', validators=[Optional(), Length(max=20)])
    description = TextAreaField('Description', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        # Populate category choices
        categories = Category.query.filter_by(is_active=True).all()
        self.category.choices = [('', 'Select Category')] + [
            (cat.name, cat.name) for cat in categories
        ]
        # Populate department choices
        departments = Department.query.filter_by(is_active=True).all()
        self.department.choices = [('', 'Select Department')] + [
            (dept.code, dept.name) for dept in departments
        ]


class SearchForm(FlaskForm):
    """Search form"""
    query = StringField('Search', validators=[DataRequired()])


class ReviewForm(FlaskForm):
    """Review form"""
    rating = SelectField('Rating', choices=[
        ('5', '5 Stars'),
        ('4', '4 Stars'),
        ('3', '3 Stars'),
        ('2', '2 Stars'),
        ('1', '1 Star')
    ], validators=[DataRequired()])
    review_text = TextAreaField('Review', validators=[Optional(), Length(max=1000)])
