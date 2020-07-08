import os
import secrets
from flask import render_template, url_for, flash, redirect, request
from dev_answer import app, db, bcrypt
from dev_answer.forms import RegistrationForm, LoginForm, UpdateProfileForm
from dev_answer.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
        

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/about")
def about():
    return render_template('about.html', title='About Us')

@app.route("/rules")
def rules():
    return render_template('rules.html', title='Rules & Terms Of Ues')

@app.route("/support")
def support():
    return render_template('support.html', title='Support')

@app.route("/ask_question")
def ask_question():
    return render_template('ask.html', title='Ask Question')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fullname=form.fullname.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created successfully! You can now log in')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign Up', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form= LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('login unsuccessful, please check your email and password!')
    return render_template('login.html', title='Sign In', form=form)        


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_picts', picture_fn)

    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.fullname = form.fullname.data
        current_user.email = form.email.data
        db.session.commit()
        flash('you account has been updated successfully !')
        return redirect(url_for('profile'))
    elif request.method == 'GET': 
        form.fullname.data = current_user.fullname
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_picts/')
    return render_template('profile.html', title='Your Profile', image_file=image_file, form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))