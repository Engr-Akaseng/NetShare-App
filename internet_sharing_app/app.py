from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import json

# ---------------------- Initialize Flask App ----------------------
app = Flask(__name__)
app.secret_key = 'password123'  # Change this to a secure random secret key in production
app.config['SECRET_KEY'] = app.secret_key

# ---------------------- MongoDB connection ----------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["internet_sharing_db"]
users_collection = db["users"]  # MongoDB collection for users

# ---------------------- Login Manager Setup ----------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ---------------------- User Class ----------------------
class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc['_id'])
        self.username = user_doc['username']
        # Add more attributes here if needed

@login_manager.user_loader
def load_user(user_id):
    user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_doc:
        return User(user_doc)
    return None

# ---------------------- Import and Register Blueprints ----------------------
from admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

# ---------------------- Routes ----------------------

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please fill out both fields.', 'danger')
            return redirect(url_for('register'))

        if users_collection.find_one({"username": username}):
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        users_collection.insert_one({"username": username, "password": hashed_pw})
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user_doc = users_collection.find_one({"username": username})
        if user_doc and check_password_hash(user_doc['password'], password):
            user = User(user_doc)
            login_user(user)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=current_user.username)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/checkout/<plan>')
@login_required
def checkout(plan):
    return render_template('checkout.html', selected_plan=plan)

@app.route('/custom_plan', methods=['POST'])
def custom_plan():
    name = request.form['name']
    email = request.form['email']
    speed = request.form['speed']
    duration = request.form['duration']
    notes = request.form['notes']

    print(f"[Custom Plan Request] From: {name} ({email})\nSpeed: {speed}, Duration: {duration}, Notes: {notes}")
    flash('Thank you! Your custom plan request has been received. We will get back to you shortly.', 'success')
    return redirect(url_for('services'))

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    print(f"[Message Received]\nFrom: {name} ({email})\nSubject: {subject}\nMessage: {message}")
    flash('Your message has been sent successfully. We will get back to you shortly.', 'success')
    return redirect(url_for('contact'))

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    bot_reply = get_bot_response(user_msg)

    with open('chat_log.txt', "a") as log:
        log.write(f"User: {user_msg}\nBot: {bot_reply}\n\n")

    return jsonify({"reply": bot_reply})

# ---------------------- Utility Functions ----------------------

def get_bot_response(user_message):
    message = user_message.lower()
    if "hello" in message or "hi" in message:
        return "Hi there! How can I assist you today?"
    elif "internet" in message:
        return "Our internet sharing service allows you to buy a config file and browse freely."
    elif "price" in message:
        return "Prices vary based on usage. Visit the pricing page for details."
    else:
        return "Thanks for your message. We'll respond shortly."

# ---------------------- Run the App ----------------------

if __name__ == '__main__':
    app.run(debug=True)
