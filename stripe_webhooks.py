from flask import Blueprint, request, jsonify, current_app
import stripe
from db import db, User, Subscription
from datetime import datetime


webhook_routes = Blueprint('webhooks', __name__)

@webhook_routes.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, current_app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': str(e)}), 400
    
    # Handle subscription events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
    elif event['type'] == 'invoice.paid':
        invoice = event['data']['object']
        handle_invoice_paid(invoice)
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_payment_failed(invoice)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    
    return jsonify({'success': True})

def handle_checkout_session(session):
    customer_email = session['customer_details']['email']
    subscription_id = session['subscription']
    
    user = User.query.filter_by(email=customer_email).first()
    if not user:
        return
    
    plan = None
    if session['metadata'].get('plan'):
        plan = session['metadata']['plan']
    else:
        # Fallback to check line items
        line_items = stripe.checkout.Session.list_line_items(session['id'])
        if line_items and line_items.data:
            price_id = line_items.data[0].price.id
            if 'starter' in price_id:
                plan = 'Starter'
            elif 'pro' in price_id:
                plan = 'Pro'
            elif 'elite' in price_id:
                plan = 'Elite'
    
    if not plan:
        return
    
    # Create or update subscription
    if not user.subscription:
        user.subscription = Subscription(
            stripe_subscription_id=subscription_id,
            plan=plan,
            monthly_limit=get_limit_for_plan(plan),
            renewal_date=datetime.fromtimestamp(session['expires_at']) if session.get('expires_at') else None
        )
    else:
        user.subscription.stripe_subscription_id = subscription_id
        user.subscription.plan = plan
        user.subscription.monthly_limit = get_limit_for_plan(plan)
        user.subscription.active = True
    
    db.session.commit()

def handle_invoice_paid(invoice):
    subscription_id = invoice['subscription']
    subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
    if subscription:
        subscription.renewal_date = datetime.fromtimestamp(invoice['period_end'])
        subscription.active = True
        db.session.commit()

def handle_payment_failed(invoice):
    subscription_id = invoice['subscription']
    subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
    if subscription:
        subscription.active = False
        db.session.commit()

def handle_subscription_deleted(subscription):
    sub = Subscription.query.filter_by(stripe_subscription_id=subscription['id']).first()
    if sub:
        sub.active = False
        db.session.commit()

def get_limit_for_plan(plan_name):
    plans = {
        'Starter': 100,
        'Pro': 500,
        'Elite': 2000
    }
    return plans.get(plan_name, 100)
