from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from app.extensions import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login.html')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard_page'))
    return render_template('login.html')

@auth_bp.route('/register.html')
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard_page'))
    return render_template('register.html')

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'client') 

    if email and User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email вже зайнятий!'})
    
    if User.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': 'Це ім\'я вже зайняте!'})

    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(name=name, email=email, password=hashed_pw, role=role)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    login_input = data.get('email') 
    password = data.get('password')

    user = User.query.filter(or_(User.email == login_input, User.name == login_input)).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Невірний логін або пароль'})

@auth_bp.route('/api/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))