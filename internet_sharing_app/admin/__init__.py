from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from bson.objectid import ObjectId

admin_bp = Blueprint('admin', __name__, template_folder='templates')

# We'll import the MongoDB client from your main app by importing db and users_collection
# Or just pass the client in __init__ if you refactor (simplified here):
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["internet_sharing_db"]
users_collection = db["users"]

# Simple admin check decorator
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please login first.", "warning")
            return redirect(url_for('login'))
        user_doc = users_collection.find_one({"_id": ObjectId(current_user.id)})
        if not user_doc or user_doc.get("role") != "admin":
            flash("Admin access only.", "danger")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def admin_index():
    return render_template('admin/index.html')

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = list(users_collection.find({}, {"password": 0}))  # Hide password hashes
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/delete/<user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        flash("You cannot delete yourself!", "danger")
        return redirect(url_for('admin.manage_users'))

    users_collection.delete_one({"_id": ObjectId(user_id)})
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin.manage_users'))
