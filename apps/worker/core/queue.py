import redis
from rq import Queue, Connection, Worker
from rq.job import Job
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
import logging
from .config import worker_settings

logger = logging.getLogger(__name__)

# Redis connection
redis_conn = redis.from_url(worker_settings.REDIS_URL)

# Queue definitions
HIGH_PRIORITY_QUEUE = Queue('high', connection=redis_conn)
DEFAULT_QUEUE = Queue('default', connection=redis_conn)
LOW_PRIORITY_QUEUE = Queue('low', connection=redis_conn)

# Queue mapping for easy access
QUEUES = {
    'high': HIGH_PRIORITY_QUEUE,
    'default': DEFAULT_QUEUE,
    'low': LOW_PRIORITY_QUEUE,
}


class JobManager:
    """Manager for RQ jobs and queues"""

    @staticmethod
    def enqueue_job(
        func: callable,
        args: tuple = (),
        kwargs: dict = None,
        queue: str = 'default',
        job_timeout: int = 300,
        retry_attempts: int = 3,
        delay: Optional[timedelta] = None
    ) -> Job:
        """Enqueue a job for background processing"""
        if kwargs is None:
            kwargs = {}

        selected_queue = QUEUES.get(queue, DEFAULT_QUEUE)

        # Add job metadata
        job_kwargs = {
            'timeout': job_timeout,
            'retry': retry_attempts,
            'meta': {
                'enqueued_at': datetime.utcnow().isoformat(),
                'queue': queue,
                'retry_attempts': retry_attempts
            }
        }

        if delay:
            job_kwargs['delay'] = delay

        job = selected_queue.enqueue(func, *args, **kwargs, **job_kwargs)
        logger.info(f"Enqueued job {job.id} in queue '{queue}'")
        return job

    @staticmethod
    def get_job(job_id: str) -> Optional[Job]:
        """Get job by ID"""
        try:
            return Job.fetch(job_id, connection=redis_conn)
        except Exception as e:
            logger.error(f"Error fetching job {job_id}: {e}")
            return None

    @staticmethod
    def get_queue_stats() -> Dict[str, Any]:
        """Get statistics for all queues"""
        stats = {}
        for name, queue in QUEUES.items():
            stats[name] = {
                'pending': len(queue),
                'started': queue.started_job_registry.count,
                'finished': queue.finished_job_registry.count,
                'failed': queue.failed_job_registry.count,
                'deferred': queue.deferred_job_registry.count,
            }
        return stats

    @staticmethod
    def get_failed_jobs(queue: str = 'default') -> List[Job]:
        """Get failed jobs from a queue"""
        selected_queue = QUEUES.get(queue, DEFAULT_QUEUE)
        return selected_queue.failed_job_registry.get_job_ids()

    @staticmethod
    def retry_failed_job(job_id: str) -> bool:
        """Retry a failed job"""
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            if job.is_failed:
                job.retry()
                logger.info(f"Retrying job {job_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error retrying job {job_id}: {e}")
            return False

    @staticmethod
    def schedule_periodic_job(
        func: callable,
        schedule: str,
        args: tuple = (),
        kwargs: dict = None,
        queue: str = 'default'
    ) -> str:
        """Schedule a periodic job (requires rq-scheduler)"""
        # This would integrate with rq-scheduler for cron-like scheduling
        # For now, we'll implement basic scheduling logic
        job_id = f"periodic_{func.__name__}_{schedule}"
        JobManager.enqueue_job(func, args, kwargs or {}, queue)
        return job_id


class EventPublisher:
    """Publisher for application events that trigger jobs"""

    @staticmethod
    def publish_event(event_type: str, payload: Dict[str, Any], queue: str = 'default'):
        """Publish an event that will be processed by workers"""
        from .events import process_event

        JobManager.enqueue_job(
            process_event,
            args=(event_type, payload),
            queue=queue,
            job_timeout=60
        )
        logger.info(f"Published event '{event_type}' to queue '{queue}'")

    @staticmethod
    def client_created(client_data: Dict[str, Any]):
        """Event: Client was created"""
        EventPublisher.publish_event('client.created', client_data)

    @staticmethod
    def membership_expiring(membership_data: Dict[str, Any]):
        """Event: Membership is expiring"""
        EventPublisher.publish_event('membership.expiring_30d', membership_data)

    @staticmethod
    def membership_status_changed(membership_data: Dict[str, Any]):
        """Event: Membership status changed"""
        EventPublisher.publish_event('membership.status_changed', membership_data)

    @staticmethod
    def client_not_checked_in_mid_month(client_data: Dict[str, Any]):
        """Event: Client hasn't checked in mid-month"""
        EventPublisher.publish_event('client.not_checked_in_mid_month', client_data)

    @staticmethod
    def krc_meetup_announce():
        """Event: KRC meetup announcement"""
        EventPublisher.publish_event('krc_meetup_announce', {})


def create_worker(queues: List[str] = None) -> Worker:
    """Create an RQ worker"""
    if queues is None:
        queues = ['high', 'default', 'low']

    queue_objects = [QUEUES[q] for q in queues if q in QUEUES]
    return Worker(queue_objects, connection=redis_conn)