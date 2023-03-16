from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request



app = Flask(__name__)
app.secret_key = '1234'  # Replace this with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f'<Post {self.title}>'

def get_post_by_id(post_id):
    post = Post.query.get(post_id)
    return post


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Wrap the db.create_all() call in an application context
with app.app_context():
    db.create_all()



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/posting', methods=['GET', 'POST'])
@login_required
def posting():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        new_post = Post(title=title, content=content, user_id=current_user.id)

        try:
            db.session.add(new_post)
            db.session.commit()
            flash("Post submitted successfully")
            return redirect(url_for('bulletin_board'))
        except Exception as e:
            db.session.rollback()
            flash("Error submitting post")
            return redirect(url_for('posting'))

    return render_template('posting.html')

@app.route('/post/<int:post_id>')
def post_details(post_id):
    post = get_post_by_id(post_id)  # You need to implement this function to get the post by its ID
    return render_template('post_details.html', post=post)



@app.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = get_post_by_id(post_id)

    if post is None:
        flash("Post not found")
        return redirect(url_for('bulletin_board'))

    if current_user.id != post.user_id:
        flash("You are not authorized to delete this post")
        return redirect(url_for('post_details', post_id=post_id))

    try:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted successfully")
        return redirect(url_for('bulletin_board'))
    except Exception as e:
        db.session.rollback()
        flash("Error deleting post")
        return redirect(url_for('post_details', post_id=post_id))




@app.route('/bulletin_board')
def bulletin_board():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    posts = Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('bulletin_board.html', posts=posts.items, pagination=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('index'))


@app.route('/membership', methods=['GET', 'POST'])
def membership():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for('membership'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("User registration successful")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash("Error registering user")
            return redirect(url_for('membership'))

    return render_template('membership.html')

if __name__ == '__main__':
    app.run(debug=True)
