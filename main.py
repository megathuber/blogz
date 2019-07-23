from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

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
    allowed_routes = ['blog', 'login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title="Home", users=users)



@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_user=request.args.get('user')
    blog_id=request.args.get('id')
    if blog_id == None and blog_user == None:
        blogs = Blog.query.all()
        return render_template('blog.html',title="All Posts", 
            blogs=blogs)
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('entry.html', blog=blog, title='Blog Entry')
    if blog_user:
        user = User.query.get(blog_user)
        return render_template('single_user.html', user=user, blogs=user.blogs, title='User Entries')
      
    


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        owner = User.query.filter_by(username=session['user']).first()
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "Please enter a blog title"
        if not blog_body:
            body_error = "Please write a blog"
        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog.id))
        else:
            return render_template('newpost.html', title="New Blog", title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)

    return render_template('newpost.html', title="New Blog")

# Blogz To Do: 
# Create the signup, login, index, and singleUser templates.
# Code the signup, login, and index route handler functions.  
# Code the logout function to handle a POST request to /logout and 
#     redirect the user to /blog after deleting the username from the session.
# Add a 'User class' to make all the functionality possible.

@app.route('/signup', methods=['POST', 'GET'])
def signup():  
    if request.method == 'GET':
        return render_template('signup.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        vpassword = request.form['vpassword']

        un_error = ''
        pw_error = ''
        vpw_error = ''
#username verification:
        if (not username) or (username.strip() == ""):
            un_error = 'Please specify a username'
        if len(username) < 3 or len(username) > 20:
            un_error = 'Username out of range (3-20 characters)'
#password verification:        
        if (not password) or (password.strip() == ""):
            pw_error = 'Please specify a password'
        if len(password) > 0 and len(password) < 3 or len(password) > 20:
            pw_error = 'Password out of range (3-20 characters)'
#verify password error:
        if (not vpassword) or (vpassword.strip() == ""):
            vpw_error = 'Please verify your password'
            vpassword = ''
        if password != vpassword:
            vpw_error = 'Verification password does not match'
            vpassword = ''
#verify user does not already exist:
        users = User.query.filter_by(username=username).all()
        if users:
            flash('User already exists', 'error')
            return redirect('/signup')
        if not un_error and not pw_error and not vpw_error and not users:
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            session['user'] = user.username
            return redirect('/newpost')
        else:
            return render_template('signup.html', 
                username=username, un_error=un_error,
                password=password, pw_error=pw_error,
                vpassword=vpassword, vpw_error=vpw_error)
            

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username).all()
        if users:
            user = users[0]
            if password == user.password:
                session['user'] = user.username
                return redirect('/newpost')
        if not users:
            flash('Username does not exist. Either try again or go to the signup page to register a new account.', 'error')
            return redirect('/login')
        else:
            flash('Username or password incorrect', 'error')
            return redirect('/login')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    del session['user']
    return redirect('/blog')



if __name__ == '__main__':
    app.run()