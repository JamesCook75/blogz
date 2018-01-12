from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'iewgbaklsjhd'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    # owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body
 
@app.route('/', methods=['GET'])
def index():
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/blog', methods=['GET'])
def blog():
    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog_item.html', blog=blog)
    return redirect('/')

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    title_error = ''
    body_error = ''

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        if not blog_title:
            title_error = 'Title cannot be blank'
        if not blog_body:
            body_error = 'Blog cannot be blank'
        if title_error or body_error:
            return render_template('newpost.html', 
                old_title=blog_title, old_body=blog_body, 
                title_error=title_error, body_error=body_error)
        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()
        return render_template('blog_item.html', blog=new_blog)
    
    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()