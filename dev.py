from flask import Flask, render_template, url_for
app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)