from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime
import csv
import io
from db import db, Subscription
from scraper.email_crawler import scrape_emails

dashboard_routes = Blueprint('dashboard', __name__)

@dashboard_routes.route('/dashboard')
@login_required
def dashboard():
    subscription = current_user.subscription
    return render_template('dashboard.html', 
                         subscription=subscription,
                         usage_percentage=min(
                             (subscription.emails_scraped / subscription.monthly_limit) * 100, 
                             100
                         ) if subscription else 0)

@dashboard_routes.route('/scrape', methods=['POST'])
@login_required
def scrape():
    if not current_user.subscription or not current_user.subscription.active:
        return jsonify({'error': 'No active subscription'}), 403
    
    url = request.form.get('url')
    keyword = request.form.get('keyword', '')
    max_emails = min(int(request.form.get('max_emails', 50)), 200)
    
    if not current_user.subscription.can_scrape(max_emails):
        return jsonify({
            'error': f'Monthly limit reached ({current_user.subscription.emails_scraped}/{current_user.subscription.monthly_limit})'
        }), 403
    
    try:
        emails = scrape_emails(url, keyword, max_emails)
        current_user.subscription.emails_scraped += len(emails)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'count': len(emails),
            'emails': emails,
            'remaining': current_user.subscription.monthly_limit - current_user.subscription.emails_scraped
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_routes.route('/download-csv')
@login_required
def download_csv():
    # In a real app, you'd fetch the user's scraped emails from a database
    data = [['email@example.com', 'https://example.com/contact']]  # Example data
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Email', 'Source URL'])
    cw.writerows(data)
    
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='scraped_emails.csv'
    )
