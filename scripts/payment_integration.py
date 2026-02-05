# payment_integration.py
# Payment processing integration with Stripe
# Handles subscriptions, billing, and payment events

import os
import stripe
from datetime import datetime, timedelta
from typing import Dict, Optional
from subscription_tier import SubscriptionTier

stripe.api_key = os.getenv("STRIPE_API_KEY")


def _require_api_key() -> Optional[Dict[str, str]]:
    if not stripe.api_key:
        return {
            "success": False,
            "error": "Stripe API key not configured"
        }
    return None

class PaymentProcessor:
    """Handle payment processing and subscription management"""
    
    # Price IDs from Stripe Dashboard
    PRICE_IDS = {
        SubscriptionTier.FREE: None,  # No payment needed
        SubscriptionTier.STARTER: "price_starter_monthly_29",
        SubscriptionTier.PROFESSIONAL: "price_professional_monthly_99",
        SubscriptionTier.ENTERPRISE: None  # Custom pricing, contact sales
    }
    
    @staticmethod
    def create_customer(user_id: str, email: str, name: str = None) -> Dict:
        """Create Stripe customer for user"""
        if (error := _require_api_key()):
            return error
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={
                    'user_id': user_id,
                    'platform': 'lyra'
                },
                name=name
            )
            
            return {
                "success": True,
                "customer_id": customer.id,
                "email": email
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def create_subscription(customer_id: str, tier: SubscriptionTier) -> Dict:
        """Create subscription for customer"""
        if (error := _require_api_key()):
            return error
        price_id = PaymentProcessor.PRICE_IDS.get(tier)
        
        if not price_id:
            return {
                "success": False,
                "error": "Invalid tier or tier does not require payment"
            }
        
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                payment_behavior='default_incomplete',
                payment_settings={
                    'save_default_payment_method': 'on_subscription'
                },
                expand=['latest_invoice.payment_intent'],
                metadata={
                    'tier': tier.value
                }
            )
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def upgrade_subscription(subscription_id: str, new_tier: SubscriptionTier) -> Dict:
        """Upgrade existing subscription to new tier"""
        if (error := _require_api_key()):
            return error
        new_price_id = PaymentProcessor.PRICE_IDS.get(new_tier)
        
        if not new_price_id:
            return {
                "success": False,
                "error": "Invalid tier for upgrade"
            }
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Update subscription with new price
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': new_price_id,
                }],
                proration_behavior='always_invoice',
                metadata={
                    'tier': new_tier.value,
                    'upgraded_at': datetime.now().isoformat()
                }
            )
            
            return {
                "success": True,
                "subscription_id": updated_subscription.id,
                "new_tier": new_tier.value,
                "proration_amount": "Calculated based on remaining time"
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def cancel_subscription(subscription_id: str, immediate: bool = False) -> Dict:
        """Cancel subscription"""
        if (error := _require_api_key()):
            return error
        try:
            if immediate:
                subscription = stripe.Subscription.delete(subscription_id)
                message = "Subscription cancelled immediately"
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
                message = "Subscription will cancel at period end"
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "status": subscription.status,
                "message": message,
                "period_end": subscription.current_period_end
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_subscription_status(subscription_id: str) -> Dict:
        """Get current subscription status"""
        if (error := _require_api_key()):
            return error
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "success": True,
                "status": subscription.status,
                "current_period_end": datetime.fromtimestamp(
                    subscription.current_period_end
                ).isoformat(),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "tier": subscription.metadata.get('tier', 'unknown')
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def create_checkout_session(customer_id: str, tier: SubscriptionTier,
                                success_url: str, cancel_url: str) -> Dict:
        """Create Stripe Checkout session for easy payment"""
        if (error := _require_api_key()):
            return error
        price_id = PaymentProcessor.PRICE_IDS.get(tier)
        
        if not price_id:
            return {
                "success": False,
                "error": "Invalid tier"
            }
        
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'tier': tier.value
                }
            )
            
            return {
                "success": True,
                "session_id": session.id,
                "checkout_url": session.url
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def handle_webhook_event(payload: str, signature: str, webhook_secret: str) -> Dict:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            event_type = event['type']
            event_data = event['data']['object']
            
            handlers = {
                'customer.subscription.created': PaymentProcessor._handle_subscription_created,
                'customer.subscription.updated': PaymentProcessor._handle_subscription_updated,
                'customer.subscription.deleted': PaymentProcessor._handle_subscription_deleted,
                'invoice.payment_succeeded': PaymentProcessor._handle_payment_succeeded,
                'invoice.payment_failed': PaymentProcessor._handle_payment_failed,
            }
            
            handler = handlers.get(event_type)
            if handler:
                return handler(event_data)
            
            return {"success": True, "message": f"Unhandled event type: {event_type}"}
            
        except stripe.error.SignatureVerificationError:
            return {
                "success": False,
                "error": "Invalid signature"
            }
    
    @staticmethod
    def _handle_subscription_created(data: Dict) -> Dict:
        """Handle subscription created event"""
        return {
            "action": "subscription_created",
            "subscription_id": data['id'],
            "customer_id": data['customer'],
            "tier": data['metadata'].get('tier'),
            "message": "Activate user's subscription tier"
        }
    
    @staticmethod
    def _handle_subscription_updated(data: Dict) -> Dict:
        """Handle subscription updated event"""
        return {
            "action": "subscription_updated",
            "subscription_id": data['id'],
            "status": data['status'],
            "message": "Update user's subscription status"
        }
    
    @staticmethod
    def _handle_subscription_deleted(data: Dict) -> Dict:
        """Handle subscription cancelled event"""
        return {
            "action": "subscription_deleted",
            "subscription_id": data['id'],
            "message": "Downgrade user to FREE tier"
        }
    
    @staticmethod
    def _handle_payment_succeeded(data: Dict) -> Dict:
        """Handle successful payment"""
        return {
            "action": "payment_succeeded",
            "invoice_id": data['id'],
            "amount": data['amount_paid'] / 100,  # Convert cents to dollars
            "message": "Payment successful, maintain access"
        }
    
    @staticmethod
    def _handle_payment_failed(data: Dict) -> Dict:
        """Handle failed payment"""
        return {
            "action": "payment_failed",
            "invoice_id": data['id'],
            "message": "Send payment retry notification to user",
            "next_attempt": data.get('next_payment_attempt')
        }

class BillingManager:
    """Manage billing and usage tracking"""
    
    def __init__(self, user_id: str, tier: SubscriptionTier):
        self.user_id = user_id
        self.tier = tier
        self.usage_this_period = {
            "requests": 0,
            "tokens": 0,
            "storage_mb": 0
        }
    
    def calculate_usage_cost(self) -> Dict:
        """Calculate overage costs for Enterprise tier"""
        base_costs = {
            SubscriptionTier.STARTER: 29,
            SubscriptionTier.PROFESSIONAL: 99,
            SubscriptionTier.ENTERPRISE: 499  # Base enterprise price
        }
        
        base_cost = base_costs.get(self.tier, 0)
        
        # Enterprise overage pricing
        overage_cost = 0
        if self.tier == SubscriptionTier.ENTERPRISE:
            # $0.01 per request over 10,000
            if self.usage_this_period["requests"] > 10000:
                overage_requests = self.usage_this_period["requests"] - 10000
                overage_cost += overage_requests * 0.01
            
            # $0.50 per GB storage over 100GB
            if self.usage_this_period["storage_mb"] > 102400:  # 100GB in MB
                overage_gb = (self.usage_this_period["storage_mb"] - 102400) / 1024
                overage_cost += overage_gb * 0.50
        
        return {
            "base_cost": base_cost,
            "overage_cost": round(overage_cost, 2),
            "total_cost": round(base_cost + overage_cost, 2),
            "currency": "USD",
            "period": "monthly"
        }
    
    def generate_invoice(self) -> Dict:
        """Generate invoice for current period"""
        costs = self.calculate_usage_cost()
        
        return {
            "user_id": self.user_id,
            "tier": self.tier.value,
            "period_start": datetime.now().replace(day=1).isoformat(),
            "period_end": (datetime.now() + timedelta(days=30)).replace(day=1).isoformat(),
            "usage": self.usage_this_period,
            "costs": costs,
            "tax": round(costs["total_cost"] * 0.08, 2),  # 8% tax example
            "total_due": round(costs["total_cost"] * 1.08, 2)
        }
