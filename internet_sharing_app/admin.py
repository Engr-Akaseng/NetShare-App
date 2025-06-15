from flask import Blueprint, render_template

admin_bp = Blueprint('admin_bp', __name__, template_folder='templates/admin')

@admin_bp.route('/')
def admin_index():
    return render_template('index.html')
