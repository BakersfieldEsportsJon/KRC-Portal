from typing import Dict, Any
import logging
from .config import worker_settings

logger = logging.getLogger(__name__)


def process_event(event_type: str, payload: Dict[str, Any]):
    """Main event processor that routes events to appropriate handlers"""
    logger.info(f"Processing event: {event_type}")

    try:
        # Route to appropriate handler
        if event_type == 'client.created':
            handle_client_created(payload)
        elif event_type == 'membership.expiring_30d':
            handle_membership_expiring(payload)
        elif event_type == 'membership.status_changed':
            handle_membership_status_changed(payload)
        elif event_type == 'client.not_checked_in_mid_month':
            handle_client_not_checked_in(payload)
        elif event_type == 'krc_meetup_announce':
            handle_krc_meetup_announce(payload)
        else:
            logger.warning(f"Unknown event type: {event_type}")

    except Exception as e:
        logger.error(f"Error processing event {event_type}: {e}")
        raise


def handle_client_created(payload: Dict[str, Any]):
    """Handle client created event - send welcome message"""
    if not worker_settings.FEATURE_MESSAGING:
        logger.info("Messaging feature disabled, skipping welcome message")
        return

    from .messaging import send_zapier_webhook

    # Prepare welcome message payload
    welcome_payload = {
        'event': 'client_welcome',
        'client_id': payload.get('client_id'),
        'name': payload.get('name'),
        'phone': payload.get('phone'),
        'email': payload.get('email'),
        'message_type': 'welcome_sms'
    }

    send_zapier_webhook('client.created', welcome_payload)
    logger.info(f"Sent welcome message for client {payload.get('client_id')}")


def handle_membership_expiring(payload: Dict[str, Any]):
    """Handle membership expiring event - send renewal reminder"""
    if not worker_settings.FEATURE_MESSAGING:
        logger.info("Messaging feature disabled, skipping expiry reminder")
        return

    from .messaging import send_zapier_webhook

    # Prepare expiry reminder payload
    reminder_payload = {
        'event': 'membership_expiring',
        'client_id': payload.get('client_id'),
        'name': payload.get('name'),
        'phone': payload.get('phone'),
        'expires_on': payload.get('expires_on'),
        'plan_code': payload.get('plan_code'),
        'message_type': 'expiry_reminder'
    }

    send_zapier_webhook('membership.expiring_30d', reminder_payload)
    logger.info(f"Sent expiry reminder for membership {payload.get('membership_id')}")


def handle_membership_status_changed(payload: Dict[str, Any]):
    """Handle membership status change - update ggLeap groups"""
    if not worker_settings.FEATURE_GGLEAP_SYNC:
        logger.info("ggLeap sync feature disabled, skipping group update")
        return

    from .ggleap import update_client_ggleap_group

    client_id = payload.get('client_id')
    new_status = payload.get('new_status')

    if client_id and new_status:
        update_client_ggleap_group(client_id, new_status)
        logger.info(f"Updated ggLeap group for client {client_id} with status {new_status}")


def handle_client_not_checked_in(payload: Dict[str, Any]):
    """Handle client not checked in mid-month - send reminder"""
    if not worker_settings.FEATURE_MESSAGING:
        logger.info("Messaging feature disabled, skipping check-in reminder")
        return

    from .messaging import send_zapier_webhook

    # Prepare check-in reminder payload
    reminder_payload = {
        'event': 'checkin_reminder',
        'client_id': payload.get('client_id'),
        'name': payload.get('name'),
        'phone': payload.get('phone'),
        'message_type': 'checkin_reminder'
    }

    send_zapier_webhook('client.not_checked_in_mid_month', reminder_payload)
    logger.info(f"Sent check-in reminder for client {payload.get('client_id')}")


def handle_krc_meetup_announce(payload: Dict[str, Any]):
    """Handle KRC meetup announcement - send to all active members"""
    if not worker_settings.FEATURE_MESSAGING:
        logger.info("Messaging feature disabled, skipping meetup announcement")
        return

    from .messaging import send_zapier_webhook
    from .database import get_db

    # Get all active clients with SMS consent
    # This would typically involve querying the database for active members
    # For now, we'll send a general announcement

    announcement_payload = {
        'event': 'krc_meetup_announce',
        'message_type': 'meetup_announcement',
        'krc_meetup': {
            'date': payload.get('date'),
            'location': 'Bakersfield eSports Center',
            'details': 'Monthly KRC meetup - all members welcome!'
        }
    }

    send_zapier_webhook('krc_meetup_announce', announcement_payload)
    logger.info("Sent KRC meetup announcement")