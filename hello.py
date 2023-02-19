from flask import Flask, render_template

## --------- Create Flask Instance ------ ##
app = Flask(__name__)

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