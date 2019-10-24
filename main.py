from flask import Flask, request, redirect, render_template, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key='768a109a77986d0fb77db7edd56dad5d'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:imgoodhowareyou@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    blogz = db.relationship('Blog', backref='author', lazy=True)

    def __init__(self,username,password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120),nullable=False)
    body = db.Column(db.Text,nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=True)

    def __init__(self, title, body, author):

        self.title = title
        self.body = body
        self.author = author



@app.before_request
def required():
    required = ['login', 'register', 'home', 'blog']
    if request.endpoint not in required and 'username' not in session:
        flash(f"You must be logged in to do that.")
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('home.html', users=users,title='Blog Users!')
   

@app.route('/blog')
def blog():
    posts = Blog.query.all()
    num_blog = request.args.get('id')
    user_id = request.args.get('user')

    if user_id:
        posts = Blog.query.filter_by(users_id=user_id)
        return render_template('user.html', posts=posts, title="User Posts")
    if num_blog:
        posts = Blog.query.all()
        return render_template('entry.html', posts=posts, title='Build-A-Blog')
   
    return render_template('blog.html', posts=posts, title='Blog Postz')

@app.route('/newblog', methods=['POST', 'GET'])
def new_post():

    user = User.query.filter_by(username=session['username']).first()
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
            new_entry = Blog(blog_title, blog_body, user)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newblog.html', title='New Entry', title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newblog.html', title='New Entry')

@app.route("/register", methods=['GET', 'POST'])

def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        dup_user = User.query.filter_by(username=username).first()

        
        if username == '':
            flash(f"Please enter a username.")
        elif len(username)>20 or len(username)<3:
            flash(f"Please enter a valid username of 3 or more characters and less than 20 characters.")
        if password == '':
            flash(f"Please enter a password.")
        elif confirm_password != password:
            flash(f"Passwords do not match.")
        elif dup_user:
            flash(f"Sorry, user already exists.")
        else:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            return redirect('/newblog')
        return render_template('register.html', title='Register')
  
        
       
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register')

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()     
        if user and user.password == password:                      
            session['username'] = username
            flash(f"Welcome back!")
            return redirect('/newblog')
        else:
            flash(f"Login unsuccessful.")
    return render_template('login.html',title='Login')

@app.route("/logout")
def logout():
    del session["username"]
    return redirect('/blog')

if  __name__ == "__main__":
    app.run()