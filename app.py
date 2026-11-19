from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/teachers')
def teachers():
    return render_template('teachers.html')

@app.route('/discount')
def discount():
    return render_template('discount.html')

@app.route('/internship')
def internship():
    return render_template('internship.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
