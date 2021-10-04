import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar
from sqlalchemy import exc
from functools import wraps
from flask import abort


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
ckeditor = CKEditor(app)
Bootstrap(app)

# #CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL?sslmode=require", 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# #CONNECT TO LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
SALT_LENGTH = 8


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    # Creating a back track for who commented.
    comments = relationship("Comment", backref="comment_author")

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")  # # =================== \/


# #CONFIGURE TABLES
class BlogPost(db.Model):  # #                                                         ||
    __tablename__ = "blog_posts"  # #                                                  ||
    id = db.Column(db.Integer, primary_key=True)  # #                                  ||
# #                                                                                    ||
    # create Foreign Key, "users.id" the users refers to the table name of user.       ||
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # # ================ /\

    # create reference to the User object, the posts refers to the posts property in the User class.
    author = relationship("User", back_populates='posts')
    # author = db.Column(db.String(250), nullable=False)  # THIS IS NOW CREATED BY (back_populates="author")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # Creating a back track for who commented.
    comments = relationship("Comment", backref="blog")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    comment_author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    blog_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    # imaginary columns that need to be set at object creation:
    # blog
    # comment_author


if not os.path.exists('blog.db') or not os.path.exists('users.db'):
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        # print(current_user, current_user.id, '#' * 100)
        if current_user.id != 1:
            return abort(403)
        # otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)
