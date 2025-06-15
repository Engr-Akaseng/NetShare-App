from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'  # Use a secure random secret in production
USERS_FILE = 'users.json'
CHAT_LOG_FILE = 'chat_log.txt'


#============Route to handle custom plan requests=============

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
#============Route to handle custom plan requests=============

#------------------------ send message ------------------------

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    # You can extend this to save to DB or send an email
    print(f"[Message Received]\nFrom: {name} ({email})\nSubject: {subject}\nMessage: {message}")

    flash('Your message has been sent successfully. We will get back to you shortly.', 'success')
    return redirect(url_for('contact'))








# ---------------------- Utility Functions ----------------------
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# ---------------------- Login Protection Decorator ----------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------- Chatbot Logic ----------------------
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

# ---------------------- Routes ----------------------

@app.route('/')
def index():
    return redirect(url_for('home')) if 'user' in session else redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please fill out both fields.', 'danger')
            return redirect(url_for('register'))

        users = load_users()
        if username in users:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))

        users[username] = generate_password_hash(password)
        save_users(users)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        users = load_users()
        if username in users and check_password_hash(users[username], password):
            session['user'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    bot_reply = get_bot_response(user_msg)

    # Log chat
    with open(CHAT_LOG_FILE, "a") as log:
        log.write(f"User: {user_msg}\nBot: {bot_reply}\n\n")

    return jsonify({"reply": bot_reply})

# ---------------------- Pages ----------------------
@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=session['user'])

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/services')
@login_required
def services():
    return render_template('services.html')

@app.route('/pricing')
@login_required
def pricing():
    return render_template('pricing.html')

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

    
@app.route('/checkout/<plan>')
@login_required  # If you require users to be logged in
def checkout(plan):
    # You can pass additional plan data (price, features) here if needed
    return render_template('checkout.html', selected_plan=plan)




# ---------------------- Run the App ----------------------
if __name__ == '__main__':
    app.run(debug=True)
