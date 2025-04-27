from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import stripe
from config import Config


# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    stripe.api_key = app.config['STRIPE_SECRET_KEY']
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from routes import auth_routes, stripe_routes, dashboard_routes, admin_routes, webhook_routes
    app.register_blueprint(auth_routes)
    app.register_blueprint(stripe_routes)
    app.register_blueprint(dashboard_routes)
    app.register_blueprint(admin_routes)
    app.register_blueprint(webhook_routes)
    
    # User loader
    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)