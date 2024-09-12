from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, SubmitPhotoForm
from db import db  # Import db instance
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photo_stock.db'
app.config['UPLOAD_FOLDER'] = 'static/images'

# Initialize db and login_manager
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import models after initializing db
from models import User, Photo

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
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

@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_photo():
    form = SubmitPhotoForm()
    if form.validate_on_submit():
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file:
                filename = os.path.join(app.config['UPLOAD_FOLDER'], photo_file.filename)
                photo_file.save(filename)
                new_photo = Photo(image=photo_file.filename, user_id=current_user.id)
                db.session.add(new_photo)
                db.session.commit()
                flash('Photo submitted successfully!', 'success')
                return redirect(url_for('home'))
        flash('No photo uploaded. Please try again.', 'danger')
    return render_template('submit.html', form=form)

@app.route('/photo/<int:photo_id>', methods=['GET', 'POST'])
def photo_detail(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    
    if request.method == 'POST':
        if 'like' in request.form:
            photo.likes += 1
        elif 'buy' in request.form:
            flash('Pretend you have bought this photo!', 'success')
        db.session.commit()
    
    return render_template('photo_detail.html', photo=photo)

if __name__ == '__main__':
    app.run(debug=True)
