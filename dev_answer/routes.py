import os
import secrets
'''import flask_whooshalchemy as wa'''
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from dev_answer import app, db, bcrypt, mail
from dev_answer.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm, RequestResetPassForm, ResetPassForm, AnswerForm, ContactUsForm 
from dev_answer.models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['WHOOSH_BASE'] = 'whoosh'
wa.whoosh_index(app, Post)

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('home.html', posts=posts)


@app.route("/search")
def search():
    posts = Post.query.whoosh_search(request.args.get('query')).all()
    return render_template('home.html', posts=posts)    

@app.route("/python.html")
def ask_py():
    posts = Post.query.order_by(Post.date_posted.desc()).filter_by(category="Python")
    return render_template('python.html', title='Python Question', posts=posts)

@app.route("/javascript.html")
def ask_js():
    posts = Post.query.order_by(Post.date_posted.desc()).filter_by(category="JavaScript")
    return render_template('javascript.html', title='JavaScript Question', posts=posts)

@app.route("/cs.html")
def ask_cs():
    posts = Post.query.order_by(Post.date_posted.desc()).filter_by(category="C#")
    return render_template('cs.html', title='C# Question', posts=posts)        

@app.route("/about")
def about():
    return render_template('about.html', title='About Us')

@app.route("/rules")
def rules():
    return render_template('rules.html', title='Rules & Terms Of Ues')

@app.route("/support", methods=['GET', 'POST'])
def support():
    form = ContactUsForm()
    if form.validate_on_submit():
        flash("Your Message has been sent, we will contact you ASAP!")
        return redirect(url_for("home"))
    return render_template('support.html', title='Support', form=form)

@app.route("/ask_question", methods=['GET', 'POST'])
@login_required
def ask_question():
    form = PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            post = Post(title=form.title.data, category=form.category.data, content=form.content.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your question has been created!')
            return redirect(url_for('home'))
    return render_template('ask.html', title='Ask Question', page_title='Ask Your Question', 
                            legend='Here you can Ask Questions for getting help from dev community.', 
                            form=form, submit='Add Question', )

@app.route("/ask_question/<int:post_id>/edit", methods=['GET', 'POST'])
@login_required
def update_question(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = form.category.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.category.data = post.category
        form.content.data = post.content
    return render_template('ask.html', title='Edit Question', form=form, page_title='Edit Your Question', 
                            legend='Here you can Edit your Questions.', submit='Update Question')    

@app.route("/answer/<int:post_id>", methods=['GET', 'POST'])
@login_required
def answer(post_id):
    post = Post.query.get_or_404(post_id) 
    answers = Comment.query.get(post_id)  
    form = AnswerForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post_id=post.id, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash("Your Answer has been added to the post!")
        return redirect(url_for("answer", post_id=post.id))
    return render_template('answer.html', title='Answers', post=post, answers=answer, form=form)    

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
    throw, f_ext = os.path.splitext(form_picture.filename)
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
    posts = Post.query.filter_by(author=current_user)
    form = UpdateProfileForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.fullname = form.fullname.data
        current_user.email = form.email.data
        current_user.password = hashed_password 
        db.session.commit()
        flash('your account has been updated successfully !')
        return redirect(url_for('profile'))
    elif request.method == 'GET': 
        form.fullname.data = current_user.fullname
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_picts/' + current_user.image_file)
    return render_template('profile.html', title=current_user.fullname+"'"+'s'+' '+'Profile', image_file=image_file, form=form, posts=posts)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def send_reset_mail(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='midaghdour@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, click the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, you can ignore this email!
Dev-Answer team.
Have a great day
'''
    mail.send(msg)


@app.route("/request_reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetPassForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_mail(user)
        flash('An email has been sent with instructions to reset your password.')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset The Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That in an invalid or expired token')
        return redirect(url_for('reset_request'))
    form = ResetPassForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updates successfully! You can now log in with the new password')
        return redirect(url_for('login'))    
    return render_template('reset_token.html', title='Reset Your Password', form=form)

