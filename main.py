from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:firewalk@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'w117kJsyd&z3PJS'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return str(self.id)


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
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
      return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            return redirect('/login')
    else:
        return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        ver_error = ''

        if ' ' in username or username == '':
            username_error = 'invalid username.'
                  
        else:
            if len(username) > 20 or len(username) < 3:
                username_error = 'username must be between (4-19) characters.'                
        
        if ' ' in password or password == '':
            password_error = 'invalid password.' 
            password = ''
        
        elif verify == '':
            ver_error = 'please verify password' 
        
        else:
            if password != verify:
                ver_error = 'passwords do not match.'
                password = ''
                verify = ''
                        
        if not username_error and not password_error and not ver_error:
            
            existing_user = User.query.filter_by(username=username).first()           
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                return flash('This user already exists.')

        else:
            return render_template('signup.html', username=username, username_error=username_error, password=password, verify=verify, password_error=password_error, ver_error=ver_error)

    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():    
    del session ['username']
    flash('Logged Out')
    return redirect('/blog')

@app.route('/', methods=['GET'])
def index():
    

    if request.args.get('user'):
        user_id = request.args.get('user')
        user = User.query.get(user_id)
        posts = Blog.query.filter_by(owner=user).all()
        return render_template('user_page.html', posts=posts)

    else:
        users = User.query.all()
        return render_template('index.html', users=users)


@app.route('/user_page')
def user_page():
    user_id = request.args.get('user')
    user = User.query.get(user_id)
    blogs = Blog.query.filter_by(owner=user).all()
    return render_template('user_page.html', blogs=blogs)

@app.route('/blog', methods=['GET'])    
def blog():
   # posts = Blog.query.all()
   
    if request.args.get('id'):
        post_id = request.args.get('id')
        single_post = Blog.query.get(post_id) 
        return render_template('single_post.html', single_post=single_post)
    
    elif request.args.get('user'):
        user_name= request.args.get('user')
        user = User.query.filter_by(username=user_name).first()
        posts = Blog.query.filter_by(owner=user).all()
        return render_template('user_page.html', posts=posts, user=user)
    else:
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts)

   
@app.route('/newpost', methods=['GET', 'POST'])
def add_post():
    
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':

        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']

        body_error = ''
        title_error = ''

        if blog_title == '':
            title_error = 'please enter a title for your blog.'  

        if blog_body == '':
            body_error = 'please enter a blog post.'  

        if not title_error and not body_error:           
            new_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_post)
            db.session.commit()            
           
            blog = Blog.query.get(new_post.id)
            return redirect('/blog?id={0}'.format(blog))

        else:
            return render_template('newpost.html', blog_title=blog_title, title="Add Blog Entry",
            blog_body=blog_body, title_error=title_error, body_error=body_error)
        
    else:
        return render_template('newpost.html')
  
   
   

if __name__ == '__main__':
    app.run()
