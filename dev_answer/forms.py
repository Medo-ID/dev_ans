from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from dev_answer.models import User


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    category = RadioField('Categorys', choices=[('Python',' .Python'),('Javascrip',' .Javascrip'),('C#',' .C#')])
    content = TextAreaField('Describe the Question', validators=[DataRequired()])
    submit = SubmitField('Add Question')

class AnswerForm(FlaskForm):
    body = TextAreaField('Your Answer', validators=[DataRequired()]) 
    submit = SubmitField('Add Answer')   

class RegistrationForm(FlaskForm):
    fullname = StringField('Full name',
                             validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('E-mail',
                             validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=4,)])
    confirm_password = PasswordField('Confirm Password',
                             validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')               

    def validate_fullname(self, fullname):
        user = User.query.filter_by(fullname=fullname.data).first()
        if user:
            raise ValidationError('That username is already taken. Please Choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken. Please Choose a different one.')    


class LoginForm(FlaskForm):
    email = StringField('E-mail',
                             validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=4,)])
    submit = SubmitField('Login')               


class UpdateProfileForm(FlaskForm):
    fullname = StringField('Full name',
                             validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('E-mail',
                             validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=4,)])
    confirm_password = PasswordField('Confirm Password',
                             validators=[DataRequired(), EqualTo('password')])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Save Update')               

    def validate_fullname(self, fullname):
        if fullname.data != current_user.fullname:
            user = User.query.filter_by(fullname=fullname.data).first()
            if user:
                raise ValidationError('That username is already taken. Please Choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already taken. Please Choose a different one.') 


class RequestResetPassForm(FlaskForm):
    email = StringField('E-mail',
                             validators=[DataRequired(), Email()])
    submit = SubmitField('Send Request')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with this email. You must sing up first.')

class ResetPassForm(FlaskForm):
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=4,)])
    confirm_password = PasswordField('Confirm Password',
                             validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')               

class ContactUsForm(FlaskForm):
    name = StringField('Your Name',
                             validators=[DataRequired()])
    e_mail = StringField('Your E-mail',
                             validators=[DataRequired(), Email()])
    issue = StringField('Issue',
                             validators=[DataRequired()])
    description = TextAreaField('Describe Your Issue', 
                             validators=[DataRequired()])
    submit = SubmitField('Send')                   