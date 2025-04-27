from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subscription = db.relationship('Subscription', backref='user', uselist=False)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    stripe_subscription_id = db.Column(db.String(100), unique=True)
    plan = db.Column(db.String(50), nullable=False)
    monthly_limit = db.Column(db.Integer, nullable=False)
    emails_scraped = db.Column(db.Integer, default=0)
    renewal_date = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    
    def reset_usage(self):
        self.emails_scraped = 0
        self.renewal_date = datetime.utcnow() + timedelta(days=30)
        db.session.commit()
    
    def can_scrape(self, count):
        return self.active and (self.emails_scraped + count) <= self.monthly_limit
    
    def __repr__(self):
        return f'<Subscription {self.plan} for User {self.user_id}>'
