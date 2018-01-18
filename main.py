from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'iewgbaklsjhd'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request        
def require_login():
    allowed_routes =['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/", methods=['GET'])
def home():
    return redirect('/blog')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged In", 'success')
            return redirect('/newpost')
        elif not user:
            flash("User does not exist", 'error')
        else:
            flash("User password incorrect", 'error')    
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not username or not password or not verify:
            flash("One or more fields are invalid", 'error')
            return render_template('signup.html', username=username)
        if len(username) < 4:
            flash("Username must be greater than 3 characters", 'error')
            return render_template('signup.html')
        if len(password) < 4:
            flash("Username must be greater than 3 characters", 'error')
            return render_template('signup.html', username=username)
        if not existing_user and password == verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        elif password != verify:
            flash("Passwords do not match", 'error')
        else:
            flash("Username already exists", 'error')
    
    return render_template('signup.html')

@app.route('/index', methods=['GET'])
def index():
    users = User.query.order_by(User.username).all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['GET'])
def blog():
    blog_id = request.args.get('id')
    author_id = request.args.get('owner_id')
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog_item.html', blog=blog)
    if author_id:
        blogs = Blog.query.filter_by(owner_id=author_id).all()
        return render_template('single_user.html', blogs=blogs)

    blogs = Blog.query.order_by(Blog.date_time.desc()).all()
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    title_error = ''
    body_error = ''

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        if not blog_title:
            title_error = 'Title cannot be blank'
        if not blog_body:
            body_error = 'Blog cannot be blank'
        if title_error or body_error:
            return render_template('newpost.html', 
                old_title=blog_title, old_body=blog_body, 
                title_error=title_error, body_error=body_error)
        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()
        return render_template('blog_item.html', blog=new_blog)
    
    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()