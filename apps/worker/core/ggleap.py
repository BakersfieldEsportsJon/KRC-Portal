import httpx
import logging
from typing import Dict, Any, Optional
from .config import worker_settings
from .database import get_db

logger = logging.getLogger(__name__)


class GgLeapAPI:
    """ggLeap API client"""

    def __init__(self):
        self.base_url = worker_settings.GGLEAP_BASE_URL
        self.api_key = worker_settings.GGLEAP_API_KEY

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from ggLeap"""
        if not self.api_key:
            logger.warning("ggLeap API key not configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/users/{user_id}",
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    }
                )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"ggLeap API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error calling ggLeap API: {e}")
            return None

    async def add_user_to_group(self, user_id: str, group_id: str) -> bool:
        """Add user to ggLeap group"""
        if not self.api_key:
            logger.warning("ggLeap API key not configured")
            return False

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/groups/{group_id}/members",
                    json={'user_id': user_id},
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    }
                )

            if response.status_code in [200, 201]:
                logger.info(f"Added user {user_id} to group {group_id}")
                return True
            else:
                logger.error(f"Failed to add user to group: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error adding user to ggLeap group: {e}")
            return False

    async def remove_user_from_group(self, user_id: str, group_id: str) -> bool:
        """Remove user from ggLeap group"""
        if not self.api_key:
            logger.warning("ggLeap API key not configured")
            return False

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/groups/{group_id}/members/{user_id}",
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    }
                )

            if response.status_code in [200, 204]:
                logger.info(f"Removed user {user_id} from group {group_id}")
                return True
            else:
                logger.error(f"Failed to remove user from group: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error removing user from ggLeap group: {e}")
            return False


def update_client_ggleap_group(client_id: str, membership_status: str):
    """Update client's ggLeap group based on membership status"""
    if not worker_settings.FEATURE_GGLEAP_SYNC:
        logger.info("ggLeap sync feature disabled")
        return

    from modules.ggleap.models import GgleapLink, GgleapGroup, GgleapGroupType

    db = get_db()
    try:
        # Get client's ggLeap link
        ggleap_link = db.query(GgleapLink).filter(
            GgleapLink.client_id == client_id
        ).first()

        if not ggleap_link:
            logger.info(f"No ggLeap link found for client {client_id}")
            return

        # Get group mappings
        active_group = db.query(GgleapGroup).filter(
            GgleapGroup.map_key == GgleapGroupType.ACTIVE
        ).first()

        expired_group = db.query(GgleapGroup).filter(
            GgleapGroup.map_key == GgleapGroupType.EXPIRED
        ).first()

        if not active_group or not expired_group:
            logger.error("ggLeap group mappings not configured")
            return

        ggleap_api = GgLeapAPI()
        user_id = ggleap_link.ggleap_user_id

        # Determine target groups based on membership status
        if membership_status == 'active':
            # Add to active group, remove from expired group
            asyncio.run(ggleap_api.add_user_to_group(user_id, active_group.ggleap_group_id))
            asyncio.run(ggleap_api.remove_user_from_group(user_id, expired_group.ggleap_group_id))
        else:
            # Add to expired group, remove from active group
            asyncio.run(ggleap_api.add_user_to_group(user_id, expired_group.ggleap_group_id))
            asyncio.run(ggleap_api.remove_user_from_group(user_id, active_group.ggleap_group_id))

        logger.info(f"Updated ggLeap groups for client {client_id} with status {membership_status}")

    except Exception as e:
        logger.error(f"Error updating ggLeap groups for client {client_id}: {e}")
    finally:
        db.close()


def sync_all_ggleap_groups():
    """Nightly job to sync all client groups with ggLeap"""
    if not worker_settings.FEATURE_GGLEAP_SYNC:
        logger.info("ggLeap sync feature disabled")
        return

    from modules.core.clients.models import Client
    from modules.memberships.models import Membership
    from modules.ggleap.models import GgleapLink
    from sqlalchemy.orm import joinedload

    db = get_db()
    try:
        # Get all clients with ggLeap links and their current memberships
        clients_with_links = db.query(Client).options(
            joinedload(Client.memberships),
            joinedload(Client.ggleap_links)
        ).join(GgleapLink).all()

        for client in clients_with_links:
            if not client.ggleap_links:
                continue

            # Get current membership status
            current_membership = None
            for membership in client.memberships:
                if membership.is_active:
                    current_membership = membership
                    break

            status = current_membership.status if current_membership else 'expired'
            update_client_ggleap_group(str(client.id), status)

        logger.info(f"Completed ggLeap group sync for {len(clients_with_links)} clients")

    except Exception as e:
        logger.error(f"Error during ggLeap group sync: {e}")
    finally:
        db.close()


# Import asyncio for async operations
import asyncio