from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog1:NZVfW5UnVvnLygtdJ@localhost:8889/build-a-blog1'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog')
def blog():
    num_blog = request.args.get('id')
    if num_blog == None:
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts, title='Build-A-Blog')
    else:
        post = Blog.query.get(num_blog)
        return render_template('entry.html', post=post, title='Blog Entry')

@app.route('/newblog', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['title_blog']
        blog_body = request.form['new_blog_entry']
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "Please enter a blog title."
        if not blog_body:
            body_error = "Please enter a blog entry."

        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newblog.html', title='New Entry', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newblog.html', title='New Entry')

if  __name__ == "__main__":
    app.run()