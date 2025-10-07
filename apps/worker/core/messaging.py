import httpx
import hmac
import hashlib
import json
import logging
from typing import Dict, Any
from datetime import datetime
from .config import worker_settings
from .database import get_db

logger = logging.getLogger(__name__)


def send_zapier_webhook(event_type: str, payload: Dict[str, Any]):
    """Send webhook to Zapier with HMAC signature"""
    if worker_settings.ZAPIER_MODE == "dev_log":
        logger.info(f"[DEV MODE] Zapier webhook: {event_type}")
        logger.info(f"[DEV MODE] Payload: {json.dumps(payload, indent=2)}")
        return True

    if not worker_settings.ZAPIER_CATCH_HOOK_URL:
        logger.warning("Zapier webhook URL not configured")
        return False

    # Prepare the full payload
    webhook_payload = {
        'timestamp': datetime.utcnow().isoformat(),
        'event': event_type,
        'data': payload
    }

    # Convert to JSON
    payload_json = json.dumps(webhook_payload, separators=(',', ':'))

    # Create HMAC signature
    signature = None
    if worker_settings.ZAPIER_HMAC_SECRET:
        signature = hmac.new(
            worker_settings.ZAPIER_HMAC_SECRET.encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    # Prepare headers
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'BEC-CRM/1.0'
    }

    if signature:
        headers['X-Hook-Signature'] = f'sha256={signature}'

    # Store webhook attempt in database
    webhook_record = create_webhook_record(event_type, webhook_payload)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                worker_settings.ZAPIER_CATCH_HOOK_URL,
                content=payload_json,
                headers=headers
            )

        if response.status_code == 200:
            update_webhook_success(webhook_record.id, response.text)
            logger.info(f"Successfully sent Zapier webhook for event: {event_type}")
            return True
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            update_webhook_failure(webhook_record.id, error_msg)
            logger.error(f"Zapier webhook failed: {error_msg}")
            return False

    except Exception as e:
        error_msg = str(e)
        update_webhook_failure(webhook_record.id, error_msg)
        logger.error(f"Error sending Zapier webhook: {error_msg}")
        return False


def create_webhook_record(event_type: str, payload: Dict[str, Any]):
    """Create a webhook record in the database"""
    from modules.messaging.models import WebhookOut, WebhookStatus

    db = get_db()
    try:
        webhook = WebhookOut(
            event=event_type,
            payload=payload,
            status=WebhookStatus.QUEUED,
            attempt_count=1
        )
        db.add(webhook)
        db.commit()
        db.refresh(webhook)
        return webhook
    finally:
        db.close()


def update_webhook_success(webhook_id: str, zap_run_id: str = None):
    """Update webhook record as successful"""
    from modules.messaging.models import WebhookOut, WebhookStatus

    db = get_db()
    try:
        webhook = db.query(WebhookOut).filter(WebhookOut.id == webhook_id).first()
        if webhook:
            webhook.status = WebhookStatus.SENT
            webhook.sent_at = datetime.utcnow()
            webhook.zap_run_id = zap_run_id
            db.commit()
    finally:
        db.close()


def update_webhook_failure(webhook_id: str, error_message: str):
    """Update webhook record as failed"""
    from modules.messaging.models import WebhookOut, WebhookStatus

    db = get_db()
    try:
        webhook = db.query(WebhookOut).filter(WebhookOut.id == webhook_id).first()
        if webhook:
            webhook.attempt_count += 1
            webhook.last_error = error_message

            # Mark as failed if max attempts reached
            if webhook.attempt_count >= 3:
                webhook.status = WebhookStatus.FAILED
            else:
                # Retry logic would go here
                pass

            db.commit()
    finally:
        db.close()


def retry_failed_webhooks():
    """Job to retry failed webhooks"""
    from modules.messaging.models import WebhookOut, WebhookStatus

    db = get_db()
    try:
        # Get webhooks that are queued or failed with retry attempts remaining
        webhooks = db.query(WebhookOut).filter(
            WebhookOut.status.in_([WebhookStatus.QUEUED, WebhookStatus.FAILED]),
            WebhookOut.attempt_count < 3
        ).limit(50).all()

        for webhook in webhooks:
            try:
                success = send_zapier_webhook(webhook.event, webhook.payload)
                if success:
                    logger.info(f"Successfully retried webhook {webhook.id}")
                else:
                    logger.warning(f"Retry failed for webhook {webhook.id}")
            except Exception as e:
                logger.error(f"Error retrying webhook {webhook.id}: {e}")

    finally:
        db.close()


# Sample message templates for reference
MESSAGE_TEMPLATES = {
    'welcome_sms': "Welcome to Bakersfield eSports Center! Your membership is now active. Visit us to start gaming!",
    'expiry_reminder': "Hi {name}! Your BEC membership expires on {expires_on}. Renew now to keep your access active!",
    'checkin_reminder': "Hi {name}! We miss you at BEC. Come by and check in to use your membership benefits!",
    'meetup_announcement': "Join us for the monthly KRC meetup at BEC! Second Tuesday of the month. See you there!"
}