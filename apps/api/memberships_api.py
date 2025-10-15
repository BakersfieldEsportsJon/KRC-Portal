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
    total_active: int  # Active clients with valid memberships
    expiring_30_days: int  # Clients with memberships expiring in next 30 days
    expired: int  # Clients with expired memberships
    plans: dict  # Plan distribution (kept for compatibility)


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
    """Get membership statistics - counts unique clients, not memberships"""
    try:
        today = date.today()
        expiry_threshold = today + timedelta(days=30)

        # Active clients (distinct clients with memberships ending >= today)
        active_result = await db.execute(
            select(func.count(func.distinct(Membership.client_id)))
            .where(Membership.ends_on >= today)
        )
        total_active = active_result.scalar() or 0

        # Clients expiring in next 30 days (distinct clients with memberships ending between today and 30 days)
        expiring_result = await db.execute(
            select(func.count(func.distinct(Membership.client_id)))
            .where(
                Membership.ends_on >= today,
                Membership.ends_on <= expiry_threshold
            )
        )
        expiring_30_days = expiring_result.scalar() or 0

        # Expired clients (distinct clients with most recent membership expired)
        # Get clients whose latest membership has expired
        expired_result = await db.execute(
            select(func.count(func.distinct(Membership.client_id)))
            .where(Membership.ends_on < today)
        )
        expired = expired_result.scalar() or 0

        # Get plan distribution for active memberships
        plans_result = await db.execute(
            select(Membership.plan_code, func.count(func.distinct(Membership.client_id)))
            .where(Membership.ends_on >= today)
            .group_by(Membership.plan_code)
        )
        plans = {plan: count for plan, count in plans_result.all()}

        return MembershipStats(
            total_active=total_active,
            expiring_30_days=expiring_30_days,
            expired=expired,
            plans=plans
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get membership stats: {str(e)}")
