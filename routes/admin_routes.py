from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from db import db, User, Subscription
from datetime import datetime, timedelta  # don't forget to import datetime and timedelta

admin_routes = Blueprint('admin', __name__)

@admin_routes.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin.html', users=users)

@admin_routes.route('/admin/reset-usage/<int:user_id>')
@login_required
def reset_usage(user_id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    if user.subscription:
        user.subscription.reset_usage()
        flash(f'Usage reset for {user.email}', 'success')
    else:
        flash('User has no subscription', 'error')
    
    return redirect(url_for('admin.admin_dashboard'))

@admin_routes.route('/admin/upgrade-plan/<int:user_id>/<plan>')
@login_required
def upgrade_plan(user_id, plan):
    if not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    plan_details = {
        'starter': {'name': 'Starter', 'limit': 100},
        'pro': {'name': 'Pro', 'limit': 500},
        'elite': {'name': 'Elite', 'limit': 2000}
    }
    
    if plan not in plan_details:
        flash('Invalid plan', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    user = User.query.get_or_404(user_id)
    if not user.subscription:
        user.subscription = Subscription(
            plan=plan_details[plan]['name'],
            monthly_limit=plan_details[plan]['limit'],
            renewal_date=datetime.utcnow() + timedelta(days=30)
        )
    else:
        user.subscription.plan = plan_details[plan]['name']
        user.subscription.monthly_limit = plan_details[plan]['limit']
    
    db.session.commit()
    flash(f'Upgraded {user.email} to {plan_details[plan]["name"]} plan', 'success')
    return redirect(url_for('admin.admin_dashboard'))
