from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import admin_bp
from .forms import UserManagementForm, PricingForm, PopupMessageForm

# Dummy in-memory data stores for demonstration
users = [
    {'username': 'john', 'email': 'john@example.com', 'role': 'user'},
    {'username': 'alice', 'email': 'alice@example.com', 'role': 'host'},
]

pricings = [
    {'plan_name': 'Basic', 'price': 10, 'speed': '10 Mbps'},
    {'plan_name': 'Premium', 'price': 25, 'speed': '50 Mbps'},
]

popups = []

def admin_required(func):
    """Decorator to allow only admin users to access certain routes."""
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access required.', 'warning')
            return redirect(url_for('user.home'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('dashboard.html', users=users, pricings=pricings, popups=popups)

@admin_bp.route('/manage-users', methods=['GET', 'POST'])
@admin_required
def manage_users():
    form = UserManagementForm()
    if form.validate_on_submit():
        # Update or add user logic here
        flash('User updated/added successfully.', 'success')
        return redirect(url_for('admin.manage_users'))
    return render_template('manage_users.html', form=form, users=users)

@admin_bp.route('/manage-pricing', methods=['GET', 'POST'])
@admin_required
def manage_pricing():
    form = PricingForm()
    if form.validate_on_submit():
        # Add or update pricing logic here
        flash('Pricing plan updated/added successfully.', 'success')
        return redirect(url_for('admin.manage_pricing'))
    return render_template('manage_pricing.html', form=form, pricings=pricings)

@admin_bp.route('/popups', methods=['GET', 'POST'])
@admin_required
def manage_popups():
    form = PopupMessageForm()
    if form.validate_on_submit():
        popup = {
            'title': form.title.data,
            'message': form.message.data
        }
        popups.append(popup)
        flash('Popup message posted.', 'success')
        return redirect(url_for('admin.manage_popups'))
    return render_template('manage_popups.html', form=form, popups=popups)

@admin_bp.route('/popups/delete/<int:index>', methods=['POST'])
@admin_required
def delete_popup(index):
    try:
        popups.pop(index)
        flash('Popup message deleted.', 'success')
    except IndexError:
        flash('Popup message not found.', 'danger')
    return redirect(url_for('admin.manage_popups'))
