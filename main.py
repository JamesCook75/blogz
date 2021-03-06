from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy, Pagination
from models import User, Blog
from app import db, app
from hashutils import check_pw_hash


@app.before_request        
def require_login():
    allowed_routes =['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/", methods=['GET'])
def home():
    return redirect('/index')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
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

@app.route('/blog/<int:page>', methods=['GET'])
def blog(page):
    per_page = 5
    blog_id = request.args.get('id')
    author_id = request.args.get('owner_id')
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog_item.html', blog=blog)
    if author_id:
        blogs = Blog.query.filter_by(owner_id=author_id).order_by(Blog.date_time.desc()).all()
        return render_template('single_user.html', blogs=blogs)

    blogs = Blog.query.order_by(Blog.date_time.desc()).paginate(per_page=per_page, page=page, error_out=True)
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