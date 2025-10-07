from .router import router
from .models import CheckIn
import logging

logger = logging.getLogger(__name__)


class KioskModule:
    """Kiosk module"""

    def __init__(self, config: dict):
        self.config = config
        self.router = router

    async def cleanup(self):
        """Cleanup module resources"""
        logger.info("Kiosk module cleanup complete")


async def init_module(config: dict) -> KioskModule:
    """Initialize the kiosk module"""
    logger.info("Initializing kiosk module")
    return KioskModule(config)