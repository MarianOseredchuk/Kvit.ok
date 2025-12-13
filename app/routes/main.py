from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index.html')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard.html')
@login_required
def dashboard_page():
    return render_template('dashboard.html')