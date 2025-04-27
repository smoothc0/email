from flask import Blueprint, redirect, url_for, current_app
import stripe

stripe_routes = Blueprint('stripe', __name__)

@stripe_routes.route('/checkout/<plan>')
def checkout(plan):
    plans = {
        'starter': {
            'price': 'price_123_starter',
            'name': 'Starter Plan'
        },
        'pro': {
            'price': 'price_456_pro',
            'name': 'Pro Plan'
        },
        'elite': {
            'price': 'price_789_elite',
            'name': 'Elite Plan'
        }
    }
    
    selected_plan = plans.get(plan)
    if not selected_plan:
        return redirect(url_for('pricing'))
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': selected_plan['price'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('stripe.success', _external=True),
            cancel_url=url_for('pricing', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        current_app.logger.error(f"Stripe error: {str(e)}")
        return redirect(url_for('pricing'))
