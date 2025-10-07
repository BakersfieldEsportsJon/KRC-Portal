from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Dict, Tuple
from uuid import UUID
from datetime import date, timedelta
from core.exceptions import NotFoundError, ValidationError
from .models import Membership
from modules.core_clients.models import Client
from .schemas import MembershipCreate, MembershipUpdate, ExpiringMembershipsRequest
import logging

logger = logging.getLogger(__name__)


class MembershipService:
    """Membership management service"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_membership(self, membership_data: MembershipCreate) -> Membership:
        """Create a new membership for a client"""
        # Verify client exists
        client_stmt = select(Client).where(Client.id == membership_data.client_id)
        client_result = await self.db.execute(client_stmt)
        client = client_result.scalar_one_or_none()

        if not client:
            raise NotFoundError("Client", str(membership_data.client_id))

        # Check for overlapping active memberships
        overlap_stmt = select(Membership).where(
            and_(
                Membership.client_id == membership_data.client_id,
                or_(
                    and_(
                        Membership.starts_on <= membership_data.ends_on,
                        Membership.ends_on >= membership_data.starts_on
                    )
                )
            )
        )
        overlap_result = await self.db.execute(overlap_stmt)
        overlapping = overlap_result.scalar_one_or_none()

        if overlapping:
            raise ValidationError(f"Membership overlaps with existing membership from {overlapping.starts_on} to {overlapping.ends_on}")

        # Create membership
        membership = Membership(
            client_id=membership_data.client_id,
            plan_code=membership_data.plan_code,
            starts_on=membership_data.starts_on,
            ends_on=membership_data.ends_on,
            notes=membership_data.notes
        )

        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        logger.info(f"Created membership {membership.plan_code} for client {membership_data.client_id}")
        return membership

    async def get_membership_by_id(self, membership_id: UUID) -> Optional[Membership]:
        """Get membership by ID"""
        stmt = select(Membership).options(
            joinedload(Membership.client)
        ).where(Membership.id == membership_id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_client_membership(self, client_id: UUID) -> Optional[Membership]:
        """Get current/latest membership for a client"""
        stmt = select(Membership).where(
            Membership.client_id == client_id
        ).order_by(Membership.created_at.desc())

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_client_memberships(self, client_id: UUID) -> List[Membership]:
        """Get all memberships for a client"""
        stmt = select(Membership).where(
            Membership.client_id == client_id
        ).order_by(Membership.created_at.desc())

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_membership(self, membership_id: UUID, membership_data: MembershipUpdate) -> Membership:
        """Update membership information"""
        membership = await self.get_membership_by_id(membership_id)
        if not membership:
            raise NotFoundError("Membership", str(membership_id))

        # Update fields
        update_data = membership_data.dict(exclude_unset=True)

        # Validate date changes
        new_starts_on = update_data.get('starts_on', membership.starts_on)
        new_ends_on = update_data.get('ends_on', membership.ends_on)

        if new_ends_on <= new_starts_on:
            raise ValidationError("End date must be after start date")

        # Check for overlapping memberships if dates are changing
        if 'starts_on' in update_data or 'ends_on' in update_data:
            overlap_stmt = select(Membership).where(
                and_(
                    Membership.client_id == membership.client_id,
                    Membership.id != membership_id,
                    or_(
                        and_(
                            Membership.starts_on <= new_ends_on,
                            Membership.ends_on >= new_starts_on
                        )
                    )
                )
            )
            overlap_result = await self.db.execute(overlap_stmt)
            overlapping = overlap_result.scalar_one_or_none()

            if overlapping:
                raise ValidationError(f"Membership overlaps with existing membership from {overlapping.starts_on} to {overlapping.ends_on}")

        # Apply updates
        for field, value in update_data.items():
            setattr(membership, field, value)

        await self.db.commit()
        await self.db.refresh(membership)
        logger.info(f"Updated membership {membership_id}")
        return membership

    async def delete_membership(self, membership_id: UUID) -> bool:
        """Delete membership"""
        membership = await self.get_membership_by_id(membership_id)
        if not membership:
            raise NotFoundError("Membership", str(membership_id))

        await self.db.delete(membership)
        await self.db.commit()
        logger.info(f"Deleted membership {membership_id}")
        return True

    async def get_expiring_memberships(self, days: int = 30, plan_codes: Optional[List[str]] = None) -> List[Membership]:
        """Get memberships expiring within specified days"""
        cutoff_date = date.today() + timedelta(days=days)

        conditions = [
            Membership.ends_on <= cutoff_date,
            Membership.ends_on >= date.today()  # Not already expired
        ]

        if plan_codes:
            conditions.append(Membership.plan_code.in_(plan_codes))

        stmt = select(Membership).options(
            joinedload(Membership.client)
        ).where(and_(*conditions)).order_by(Membership.ends_on)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_membership_stats(self) -> Dict:
        """Get membership statistics"""
        today = date.today()

        # Count by status
        active_count = await self.db.scalar(
            select(func.count(Membership.id)).where(
                and_(Membership.starts_on <= today, Membership.ends_on >= today)
            )
        )

        expired_count = await self.db.scalar(
            select(func.count(Membership.id)).where(Membership.ends_on < today)
        )

        pending_count = await self.db.scalar(
            select(func.count(Membership.id)).where(Membership.starts_on > today)
        )

        # Count expiring soon
        expiring_30_count = await self.db.scalar(
            select(func.count(Membership.id)).where(
                and_(
                    Membership.ends_on >= today,
                    Membership.ends_on <= today + timedelta(days=30)
                )
            )
        )

        expiring_7_count = await self.db.scalar(
            select(func.count(Membership.id)).where(
                and_(
                    Membership.ends_on >= today,
                    Membership.ends_on <= today + timedelta(days=7)
                )
            )
        )

        # Count by plan
        plan_counts_stmt = select(
            Membership.plan_code,
            func.count(Membership.id).label('count')
        ).where(
            and_(Membership.starts_on <= today, Membership.ends_on >= today)
        ).group_by(Membership.plan_code)

        plan_result = await self.db.execute(plan_counts_stmt)
        plans = {row.plan_code: row.count for row in plan_result}

        return {
            "total_active": active_count or 0,
            "total_expired": expired_count or 0,
            "total_pending": pending_count or 0,
            "expiring_30_days": expiring_30_count or 0,
            "expiring_7_days": expiring_7_count or 0,
            "plans": plans
        }

    async def get_memberships_by_status(self, status: str, limit: int = 100, offset: int = 0) -> Tuple[List[Membership], int]:
        """Get memberships filtered by status"""
        today = date.today()

        if status == "active":
            conditions = [Membership.starts_on <= today, Membership.ends_on >= today]
        elif status == "expired":
            conditions = [Membership.ends_on < today]
        elif status == "pending":
            conditions = [Membership.starts_on > today]
        else:
            raise ValidationError(f"Invalid status: {status}")

        # Count query
        count_stmt = select(func.count(Membership.id)).where(and_(*conditions))
        total_count = await self.db.scalar(count_stmt)

        # Data query
        stmt = select(Membership).options(
            joinedload(Membership.client)
        ).where(and_(*conditions)).order_by(
            Membership.ends_on if status in ["active", "expired"] else Membership.starts_on
        ).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        memberships = list(result.scalars().all())

        return memberships, total_count or 0