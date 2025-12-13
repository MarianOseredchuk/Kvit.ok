from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import User, Event

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard_page'))
    return render_template('admin.html')

@admin_bp.route('/api/admin/users')
@login_required
def get_all_users():
    if current_user.role != 'admin': return jsonify([]), 403
    users = User.query.all()
    result = []
    for u in users:
        result.append({'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role})
    return jsonify(result)

@admin_bp.route('/api/admin/update_event/<int:event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    if current_user.role != 'admin': return jsonify({'success': False, 'message': 'Доступ заборонено'}), 403
    event = Event.query.get(event_id)
    if not event: return jsonify({'success': False, 'message': 'Подію не знайдено'})
    data = request.get_json()
    try:
        event.title = data.get('title')
        event.date = data.get('date')
        event.time = data.get('time')
        event.location = data.get('location')
        event.price = int(data.get('price'))
        event.total_seats = int(data.get('total_seats'))
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/api/admin/delete_event/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    if current_user.role != 'admin': return jsonify({'success': False, 'message': 'Доступ заборонено'}), 403
    event = Event.query.get(event_id)
    if not event: return jsonify({'success': False, 'message': 'Не знайдено'})
    try:
        event.attendees = [] 
        db.session.delete(event)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/api/admin/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin': return jsonify({'success': False, 'message': 'Доступ заборонено'}), 403
    user = User.query.get(user_id)
    if not user: return jsonify({'success': False, 'message': 'Не знайдено'})
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Не можна видалити самого себе!'})
    try:
        user.booked_events = []
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})