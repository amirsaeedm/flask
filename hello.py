from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import date

## --------- Create Flask Instance ------ ##
app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = 'ASDF'  ## for CSRF forms, avoid hijacking
## --------- Add Database --------- ##
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://Analytics:Analytics_123@172.16.100.53/flask'
# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'users.db')
## --------- Initialize Database --------- ##
db = SQLAlchemy(app)
migrate = Migrate(app, db)

## ------ Create Blog Post Model ----- ##
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))  # on the url instead of numbers for users/db, put text
    
## -------- Create Posts Form --------- ##
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    author = StringField('Author', validators=[DataRequired()])
    slug = StringField('SlugField', validators=[DataRequired()])
    submit = SubmitField('Submit')

## -------- Create Database Model -------- ##
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favourite_color = db.Column(db.String(100))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ----- Passwords ----- #
    password_hash = db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute !')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # ----- Create a String ---- #
    def __repr__(self):
        return '<Name %r>' %self.name

## ---- Create User Entry Form Class ---- ##
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favourite_color = StringField('Favourite Color') # No need for validator as this Field could be blank
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must Match !')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

## ---- Create Password Form Class ---- ##
class PasswordForm(FlaskForm):
    email = StringField("What's your email", validators=[DataRequired()])
    password_hash = PasswordField("What's your password", validators=[DataRequired()])
    submit = SubmitField("Submit")

## ---- Create Form Class ---- ##
class NamerForm(FlaskForm):
    name = StringField("What's your name", validators=[DataRequired()])
    submit = SubmitField("Submit")

##--- Fileds --- ##    
# BooleanField
# DateField
# DateTimeField
# DecimalFiled
# FileField
# HiddenField
# MultipleField
# FieldList
# FloatField
# IntegerField
# PasswordField
# RadioField
# SelectField
# SelectMultipleField
# SubmitFiled
# StringFiled
# TextAreaField

##--- Validators --- ##
# DataRequired
# Email
# EqualTo
# InputRequired
# IPAddress
# Length
# MacAddress
# NumberRange
# Optional
# Regexp
# URL
# UUID
# AnyOf
# NoneOf

## --- Some Jinja Filters --- ##
# safe
# capitalize
# lower
# upper
# title
# trim
# striptags

## --------- Create route decorator ------- ##
## --------- This is useful for creating webpage routes e.g. "www.page.com/user" ----- ##
@app.route('/')
def index():
    first_name = 'Amir'
    stuff = "This is <strong>Bold</strong> Text"
    fav_pizza = ['Margeritta', "Cheese", "Fajita", 41]
    return render_template('index.html', 
                           first_name=first_name, 
                           stuff=stuff,
                           fav_pizza=fav_pizza)

## --- Example http://127.0.0.1:5000/user/amir ---- ##
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

## --- Create Custom Error Pages ---- ##
## --- Page Not Found Error ---- ##
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

## --- Internal Server Error ---- ##
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

## ---- Create Password Test Page ----- ##
@app.route('/test_pw', methods=['GET', 'POST'])  # GET a webpage, POST as form
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    ## --- Validate Form --- ##
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        
        # ----- Lookup user by email address ------ #
        pw_to_check = Users.query.filter_by(email=email).first()
        # ------- Check Hashed Password ---------- #
        passed = check_password_hash(pw_to_check.password_hash, password)
    
    return render_template('test_pw.html', 
                           email=email, 
                           password=password,
                           pw_to_check = pw_to_check,
                           passed = passed,
                           form=form)

## ---- Create Name Page ----- ##
@app.route('/name', methods=['GET', 'POST'])  # GET a webpage, POST as form
def name():
    name = None
    form = NamerForm()
    ## --- Validate Form --- ##
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Form Submitted Successfully !')
    
    return render_template('name.html', 
                           name=name, 
                           form=form)
    
## ---- Create User Entry Page ----- ##
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # ---- Hash the password ---- #
            hashed_pw = generate_password_hash(form.password_hash.data, 'sha256')
            
            user = Users(name=form.name.data, email=form.email.data, favourite_color=form.favourite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favourite_color.data = ''
        form.password_hash = ''
        flash('User Added Successfully !')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', 
                           form=form,
                           name=name,
                           our_users=our_users)

## ----- Delete Record ---- ##
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully !')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', 
                            form=form,
                            name=name,
                            our_users=our_users,
                            id=id)    
    except:
        flash('There was a problem deleting the user ... Please try again !')
        return render_template('add_user.html', 
                            form=form,
                            name=name,
                            our_users=our_users,
                            id=id)

## ----- Update Records in DB ------ ##
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST': # Can also use "form.validate_on_submit():"
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color = request.form['favourite_color']
        try:
            db.session.commit()
            flash('User updated successfully')
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)
        except:
            flash('Error! Looks like there was a problem ... Try again !')
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

## ------ Generate JSON (API) ----- ##
@app.route('/date')
def get_current_date():
    favourite_pizza = {
        "John":'Pepperoni',
        "Mary": 'Cheese',
        "Tim": 'Mushroom'
    }
    return favourite_pizza
    #return {'Date': date.today()}
    
## -------- Add Posts Page ---------- ##
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        ## -- Clear Form after Submit -- ##
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        
        ## ---- Add Post Data to DataBase ---- #
        db.session.add(post)
        db.session.commit()
        flash('Blog Post Submitted Successfully !')
        
    ## ----- Redirect to Webpage ----- #
    return render_template('add_post.html',
                           form=form)
    
## ----- Create Blogs Diplay Page ------ #
@app.route('/posts')
def posts():
    # ----- Grab all the Posts from DataBase ----- #
    posts = Posts.query.order_by(Posts.date_posted)
    
    return render_template('posts.html',
                           posts=posts)