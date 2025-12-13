import os
import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Event
from app.utils import allowed_file

events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events')
def get_events():
    events = Event.query.all()
    result = []
    for event in events:
        result.append({
            'id': event.id,
            'title': event.title,
            'date': event.date,
            'time': event.time,
            'location': event.location,
            'type': event.type,
            'price': event.price,
            'remaining_seats': event.remaining_seats,
            'description': event.description,
            'image_url': event.image_url
        })
    return jsonify(result)

@events_bp.route('/api/create_event', methods=['POST'])
@login_required
def create_event():
    if current_user.role not in ['organizer', 'admin']:
        return jsonify({'success': False, 'message': 'Доступ заборонено!'}), 403

    data = request.form
    files = request.files.getlist('images')
    saved_filenames = []
    
    for file in files:
        if file and allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
            saved_filenames.append(unique_filename)
            
    image_string = ",".join(saved_filenames)

    try:
        new_event = Event(
            title=data.get('title'),
            date=data.get('date'),
            time=data.get('time'),
            location=data.get('location'),
            type=data.get('type'),
            price=int(data.get('price', 0)),
            description=data.get('description'),
            image_url=image_string, 
            total_seats=int(data.get('total_seats', 0)),
            remaining_seats=int(data.get('remaining_seats', 0))
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@events_bp.route('/api/book_ticket', methods=['POST'])
@login_required
def book_ticket():
    data = request.get_json()
    event_id = data.get('event_id')
    
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'success': False, 'message': 'Подію не знайдено'})
        
    if event in current_user.booked_events:
        return jsonify({'success': False, 'message': 'Ви вже зареєстровані!'})
        
    if event.remaining_seats <= 0:
        return jsonify({'success': False, 'message': 'Місця закінчились.'})

    try:
        current_user.booked_events.append(event)
        event.remaining_seats -= 1
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@events_bp.route('/api/cancel_ticket', methods=['POST'])
@login_required
def cancel_ticket():
    data = request.get_json()
    event_id = data.get('event_id')
    
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'success': False, 'message': 'Подію не знайдено'})
        
    if event not in current_user.booked_events:
        return jsonify({'success': False, 'message': 'Ви не зареєстровані на цю подію!'})

    try:
        current_user.booked_events.remove(event)
        event.remaining_seats += 1
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@events_bp.route('/api/my_events')
@login_required
def get_my_events():
    events = current_user.booked_events
    result = []
    for event in events:
        result.append({
            'id': event.id,
            'title': event.title,
            'date': event.date,
            'time': event.time,
            'location': event.location,
            'type': event.type,
            'price': event.price,
            'description': event.description,
            'image_url': event.image_url
        })
    return jsonify(result)

@events_bp.route('/api/event/<int:event_id>')
def get_single_event(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify({
        'id': event.id,
        'title': event.title,
        'date': event.date,
        'time': event.time,
        'location': event.location,
        'price': event.price,
        'total_seats': event.total_seats,
        'description': event.description,
        'image_url': event.image_url
    })