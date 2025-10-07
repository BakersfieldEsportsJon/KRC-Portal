"""
Memberships API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List
from datetime import date, datetime, timedelta

from models import Membership, Client
from core.database import AsyncSessionLocal
from auth_workaround import get_current_user, User

router = APIRouter(prefix="/memberships", tags=["Memberships"])


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Schemas
class MembershipWithClient(BaseModel):
    id: str
    client_id: str
    plan_code: str
    starts_on: date
    ends_on: date
    notes: str | None
    created_at: str
    client_first_name: str
    client_last_name: str
    client_email: str | None

    class Config:
        from_attributes = True


class MembershipStats(BaseModel):
    total: int
    active: int
    expiring_soon: int
    expired: int


# Routes
@router.get("/expiring", response_model=List[MembershipWithClient])
async def get_expiring_memberships(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get memberships expiring within specified days"""
    try:
        today = date.today()
        expiry_date = today + timedelta(days=days)

        stmt = select(Membership, Client).join(
            Client, Membership.client_id == Client.id
        ).where(
            Membership.ends_on >= today,
            Membership.ends_on <= expiry_date
        ).order_by(Membership.ends_on.asc())

        result = await db.execute(stmt)
        memberships_with_clients = result.all()

        return [
            MembershipWithClient(
                id=str(membership.id),
                client_id=str(membership.client_id),
                plan_code=membership.plan_code,
                starts_on=membership.starts_on,
                ends_on=membership.ends_on,
                notes=membership.notes,
                created_at=membership.created_at.isoformat(),
                client_first_name=client.first_name,
                client_last_name=client.last_name,
                client_email=client.email
            )
            for membership, client in memberships_with_clients
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get expiring memberships: {str(e)}")


@router.get("/stats", response_model=MembershipStats)
async def get_membership_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get membership statistics"""
    try:
        today = date.today()
        expiry_threshold = today + timedelta(days=30)

        # Total memberships
        total_result = await db.execute(select(func.count(Membership.id)))
        total = total_result.scalar() or 0

        # Active memberships (not expired)
        active_result = await db.execute(
            select(func.count(Membership.id)).where(Membership.ends_on >= today)
        )
        active = active_result.scalar() or 0

        # Expiring soon (within 30 days)
        expiring_result = await db.execute(
            select(func.count(Membership.id)).where(
                Membership.ends_on >= today,
                Membership.ends_on <= expiry_threshold
            )
        )
        expiring_soon = expiring_result.scalar() or 0

        # Expired
        expired_result = await db.execute(
            select(func.count(Membership.id)).where(Membership.ends_on < today)
        )
        expired = expired_result.scalar() or 0

        return MembershipStats(
            total=total,
            active=active,
            expiring_soon=expiring_soon,
            expired=expired
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get membership stats: {str(e)}")
