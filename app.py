from flask import Flask, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['UPLOAD_FOLDER'] = 'static/images'

# In-memory data
users = {
    'user1': generate_password_hash('password1')
}
photos = [
    {'id': 1, 'image': 'default1.jpg', 'likes': 0},
    {'id': 2, 'image': 'default2.jpg', 'likes': 0},
    {'id': 3, 'image': 'default3.jpg', 'likes': 0}
]

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('home.html', photos=photos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        hashed_password = users.get(username)
        if hashed_password and check_password_hash(hashed_password, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/photo/<int:photo_id>', methods=['POST'])
def photo_action(photo_id):
    photo = next((p for p in photos if p['id'] == photo_id), None)
    if photo:
        if 'like' in request.form:
            photo['likes'] += 1
            flash('Photo liked!', 'success')
        elif 'buy' in request.form:
            flash('Pretend you have bought this photo!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

