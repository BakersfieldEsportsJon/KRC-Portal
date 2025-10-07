from .router import router
from .models import User
from .dependencies import get_current_user, require_admin, require_staff
import logging

logger = logging.getLogger(__name__)


class CoreAuthModule:
    """Core authentication module"""

    def __init__(self, config: dict):
        self.config = config
        self.router = router

    async def cleanup(self):
        """Cleanup module resources"""
        logger.info("Core auth module cleanup complete")


async def init_module(config: dict) -> CoreAuthModule:
    """Initialize the core auth module"""
    logger.info("Initializing core auth module")
    return CoreAuthModule(config)