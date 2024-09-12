from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm
from db import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photo_stock.db'

# Initialize db and login_manager
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import models after initializing db
from models import User, Photo

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()
    # Add default photos if the table is empty
    if not Photo.query.first():
        default_photos = [
            {"image": "default1.jpg", "likes": 0},
            {"image": "default2.jpg", "likes": 0},
            {"image": "default3.jpg", "likes": 0}
        ]
        for photo in default_photos:
            db.session.add(Photo(**photo))
        db.session.commit()

@app.route('/')
@login_required
def home():
    photos = Photo.query.all()
    return render_template('home.html', photos=photos)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/photo/<int:photo_id>', methods=['POST'])
@login_required
def photo_action(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    
    if 'like' in request.form:
        photo.likes += 1
        flash('Photo liked!', 'success')
    elif 'buy' in request.form:
        flash('Pretend you have bought this photo!', 'success')
    
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)