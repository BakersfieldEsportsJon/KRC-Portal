from .router import router
from .models import Membership
import logging

logger = logging.getLogger(__name__)


class MembershipsModule:
    """Memberships module"""

    def __init__(self, config: dict):
        self.config = config
        self.router = router

    async def cleanup(self):
        """Cleanup module resources"""
        logger.info("Memberships module cleanup complete")


async def init_module(config: dict) -> MembershipsModule:
    """Initialize the memberships module"""
    logger.info("Initializing memberships module")
    return MembershipsModule(config)