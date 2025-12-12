import os
import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['SECRET_KEY'] = 'secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kvitok.db'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

bookings = db.Table('bookings',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True) 
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='client')
    
    booked_events = db.relationship('Event', secondary=bookings, backref='attendees')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(50))
    time = db.Column(db.String(20))
    location = db.Column(db.String(100))
    type = db.Column(db.String(50))
    price = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, default="")
    image_url = db.Column(db.String(500)) 
    total_seats = db.Column(db.Integer, default=100)
    remaining_seats = db.Column(db.Integer)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/login.html')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))
    return render_template('login.html')

@app.route('/register.html')
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))
    return render_template('register.html')

@app.route('/dashboard.html')
@login_required
def dashboard_page():
    return render_template('dashboard.html')


@app.route('/api/register', methods=['POST'])
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

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    login_input = data.get('email') 
    password = data.get('password')

    user = User.query.filter(or_(User.email == login_input, User.name == login_input)).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Невірний логін або пароль'})

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/events')
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

@app.route('/api/create_event', methods=['POST'])
@login_required
def create_event():
    

    
    if current_user.role not in ['organizer', 'admin']:
        return jsonify({'success': False, 'message': 'Доступ заборонено!'}), 403

    data = request.form
    files = request.files.getlist('images')
    
    saved_filenames = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
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

@app.route('/api/book_ticket', methods=['POST'])
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

@app.route('/api/my_events')
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

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard_page'))
    return render_template('admin.html')

@app.route('/api/create_admin_simple', methods=['POST'])
def create_admin_simple():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    if not name or not password:
        return jsonify({'success': False, 'message': 'Потрібні ім\'я та пароль'})

    if User.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': 'Такий нікнейм вже зайнятий!'})

    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    new_admin = User(name=name, email=None, password=hashed_pw, role='admin')
    
    try:
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Адмін {name} створений успішно!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/admin/users')
@login_required
def get_all_users():
    if current_user.role != 'admin': return jsonify([]), 403
    users = User.query.all()
    result = []
    for u in users:
        result.append({'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role})
    return jsonify(result)

@app.route('/api/event/<int:event_id>')
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

@app.route('/api/admin/update_event/<int:event_id>', methods=['PUT'])
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

@app.route('/api/admin/delete_event/<int:event_id>', methods=['DELETE'])
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

@app.route('/api/admin/delete_user/<int:user_id>', methods=['DELETE'])
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)