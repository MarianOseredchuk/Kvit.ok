from flask_login import UserMixin
from app.extensions import db

# Таблиця зв'язку (Many-to-Many)
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