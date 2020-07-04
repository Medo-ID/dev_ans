from flask import render_template, url_for, flash, redirect
from dev_answer import app
from dev_answer.forms import RegistrationForm, LoginForm
from dev_answer.models import User, Post
        

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

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created successfully for {form.fullname.data}!')
        return redirect(url_for('home'))
    return render_template('register.html', title='Sign Up', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form= LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@admin.com' and form.password.data == 'admin':
            flash('You have been logged in successfully!')
            return redirect(url_for('home'))
        else:
            flash('login unsuccessful, please check your email and password!')
    return render_template('login.html', title='Sign In', form=form)        
