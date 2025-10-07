from .router import router
from .models import Client, Tag, ContactMethod, Consent
import logging

logger = logging.getLogger(__name__)


class CoreClientsModule:
    """Core clients module"""

    def __init__(self, config: dict):
        self.config = config
        self.router = router

    async def cleanup(self):
        """Cleanup module resources"""
        logger.info("Core clients module cleanup complete")


async def init_module(config: dict) -> CoreClientsModule:
    """Initialize the core clients module"""
    logger.info("Initializing core clients module")
    return CoreClientsModule(config)