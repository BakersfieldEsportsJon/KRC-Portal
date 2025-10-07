#!/usr/bin/env python3
"""
BEC CRM Worker System

Background job processor for handling:
- Membership expiry notifications
- Welcome messages for new clients
- ggLeap group synchronization
- Zapier webhook delivery
- Scheduled reminders and announcements
"""

import sys
import os
import logging
from datetime import datetime

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.config import worker_settings
from core.queue import create_worker, QUEUES
from core.scheduler import setup_scheduled_jobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/worker.log') if worker_settings.is_production else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_worker():
    """Run the RQ worker"""
    logger.info("Starting BEC CRM Worker")
    logger.info(f"Environment: {worker_settings.APP_ENV}")
    logger.info(f"Redis URL: {worker_settings.REDIS_URL}")
    logger.info(f"Features - Messaging: {worker_settings.FEATURE_MESSAGING}, ggLeap: {worker_settings.FEATURE_GGLEAP_SYNC}")

    # Create worker for all queues
    worker = create_worker(['high', 'default', 'low'])

    try:
        # Start processing jobs
        worker.work(with_scheduler=True)
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.error(f"Worker error: {e}")
        raise


def run_scheduler():
    """Run the job scheduler"""
    logger.info("Starting BEC CRM Scheduler")

    try:
        # Set up scheduled jobs
        setup_scheduled_jobs()

        # Keep the scheduler running
        from rq_scheduler import Scheduler
        from core.queue import redis_conn

        scheduler = Scheduler(connection=redis_conn)
        scheduler.run()

    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        raise


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'scheduler':
            run_scheduler()
        elif command == 'worker':
            run_worker()
        else:
            logger.error(f"Unknown command: {command}")
            sys.exit(1)
    else:
        # Default to worker
        run_worker()


if __name__ == "__main__":
    main()