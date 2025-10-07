from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
from .queue import JobManager, EventPublisher
from .messaging import retry_failed_webhooks
from .ggleap import sync_all_ggleap_groups
from .database import get_db

logger = logging.getLogger(__name__)


def schedule_membership_expiry_check():
    """Daily job to check for expiring memberships"""
    logger.info("Running membership expiry check")

    from modules.memberships.models import Membership
    from modules.core.clients.models import Client
    from sqlalchemy.orm import joinedload

    db = get_db()
    try:
        # Get memberships expiring in 30 days
        cutoff_date = datetime.now().date() + timedelta(days=30)

        expiring_memberships = db.query(Membership).options(
            joinedload(Membership.client)
        ).filter(
            Membership.ends_on <= cutoff_date,
            Membership.ends_on >= datetime.now().date()  # Not already expired
        ).all()

        for membership in expiring_memberships:
            # Publish expiry event
            EventPublisher.membership_expiring({
                'membership_id': str(membership.id),
                'client_id': str(membership.client_id),
                'name': membership.client.full_name,
                'phone': membership.client.phone,
                'email': membership.client.email,
                'expires_on': membership.ends_on.isoformat(),
                'plan_code': membership.plan_code
            })

        logger.info(f"Processed {len(expiring_memberships)} expiring memberships")

    except Exception as e:
        logger.error(f"Error in membership expiry check: {e}")
    finally:
        db.close()


def schedule_monthly_checkin_reminder():
    """Monthly job on 15th to remind clients who haven't checked in"""
    logger.info("Running monthly check-in reminder")

    from modules.core.clients.models import Client
    from modules.kiosk.models import CheckIn
    from modules.memberships.models import Membership
    from sqlalchemy.orm import joinedload
    from sqlalchemy import and_, func

    db = get_db()
    try:
        # Get start of current month
        today = datetime.now().date()
        month_start = today.replace(day=1)

        # Get active clients who haven't checked in this month
        clients_without_checkin = db.query(Client).options(
            joinedload(Client.memberships)
        ).outerjoin(
            CheckIn,
            and_(
                CheckIn.client_id == Client.id,
                func.date(CheckIn.happened_at) >= month_start
            )
        ).join(
            Membership,
            and_(
                Membership.client_id == Client.id,
                Membership.starts_on <= today,
                Membership.ends_on >= today  # Active membership
            )
        ).filter(
            CheckIn.id.is_(None)  # No check-ins this month
        ).all()

        for client in clients_without_checkin:
            if client.phone:  # Only send to clients with phone numbers
                EventPublisher.client_not_checked_in_mid_month({
                    'client_id': str(client.id),
                    'name': client.full_name,
                    'phone': client.phone,
                    'email': client.email
                })

        logger.info(f"Sent check-in reminders to {len(clients_without_checkin)} clients")

    except Exception as e:
        logger.error(f"Error in monthly check-in reminder: {e}")
    finally:
        db.close()


def schedule_krc_meetup_announcement():
    """Monthly job to announce KRC meetup (2nd Tuesday of month)"""
    logger.info("Running KRC meetup announcement")

    today = datetime.now().date()

    # Calculate 2nd Tuesday of current month
    first_day = today.replace(day=1)
    first_tuesday = first_day + timedelta(days=(1 - first_day.weekday()) % 7)
    second_tuesday = first_tuesday + timedelta(days=7)

    # Only announce on the 2nd Tuesday
    if today == second_tuesday:
        EventPublisher.krc_meetup_announce({
            'date': second_tuesday.isoformat(),
            'month': today.strftime('%B %Y')
        })
        logger.info(f"Sent KRC meetup announcement for {second_tuesday}")
    else:
        logger.info(f"Not 2nd Tuesday ({second_tuesday}), skipping meetup announcement")


def schedule_webhook_retry():
    """Hourly job to retry failed webhooks"""
    logger.info("Running webhook retry job")
    try:
        retry_failed_webhooks()
    except Exception as e:
        logger.error(f"Error in webhook retry job: {e}")


def schedule_ggleap_sync():
    """Nightly job to sync ggLeap groups"""
    logger.info("Running ggLeap group sync")
    try:
        sync_all_ggleap_groups()
    except Exception as e:
        logger.error(f"Error in ggLeap sync job: {e}")


def setup_scheduled_jobs():
    """Set up all scheduled jobs"""
    logger.info("Setting up scheduled jobs")

    # Daily jobs
    JobManager.schedule_periodic_job(
        schedule_membership_expiry_check,
        "0 9 * * *",  # Daily at 9 AM
        queue='default'
    )

    # Monthly jobs
    JobManager.schedule_periodic_job(
        schedule_monthly_checkin_reminder,
        "0 10 15 * *",  # 15th of month at 10 AM
        queue='default'
    )

    JobManager.schedule_periodic_job(
        schedule_krc_meetup_announcement,
        "0 10 * * 2",  # Every Tuesday at 10 AM (will check if it's 2nd Tuesday)
        queue='default'
    )

    # Hourly jobs
    JobManager.schedule_periodic_job(
        schedule_webhook_retry,
        "0 * * * *",  # Every hour
        queue='low'
    )

    # Nightly jobs
    JobManager.schedule_periodic_job(
        schedule_ggleap_sync,
        "0 2 * * *",  # Daily at 2 AM
        queue='low'
    )

    logger.info("Scheduled jobs setup complete")