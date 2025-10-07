"""
Check-ins API endpoints (stats and additional features)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, date
from typing import Optional
from uuid import UUID

from models import CheckIn, Client, Membership, CheckInMethod
from core.database import AsyncSessionLocal
from auth_workaround import get_current_user, User

router = APIRouter(prefix="/checkins", tags=["Check-ins"])


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Schemas
class CheckInCreate(BaseModel):
    client_id: UUID
    method: str = Field(default="staff")
    station: Optional[str] = None
    notes: Optional[str] = None


class CheckInResponse(BaseModel):
    id: str
    client_id: str
    method: str
    station: Optional[str]
    happened_at: str
    notes: Optional[str]
    created_at: str
    client_first_name: Optional[str] = None
    client_last_name: Optional[str] = None
    membership_warning: Optional[str] = None


class CheckInStats(BaseModel):
    today: int
    this_week: int
    this_month: int
    total: int


# Routes
@router.post("", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
async def create_checkin(
    checkin_data: CheckInCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a check-in for a client"""
    try:
        # Verify client exists
        result = await db.execute(select(Client).where(Client.id == checkin_data.client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # Check membership status
        today = date.today()
        expiring_threshold = today + timedelta(days=30)
        membership_warning = None

        # Get active or most recent membership
        membership_stmt = select(Membership).where(
            Membership.client_id == checkin_data.client_id
        ).order_by(Membership.ends_on.desc())

        membership_result = await db.execute(membership_stmt)
        membership = membership_result.scalar_one_or_none()

        if membership:
            if membership.ends_on < today:
                days_expired = (today - membership.ends_on).days
                membership_warning = f"Membership expired {days_expired} day{'s' if days_expired != 1 else ''} ago"
            elif membership.ends_on <= expiring_threshold:
                days_remaining = (membership.ends_on - today).days
                membership_warning = f"Membership expiring in {days_remaining} day{'s' if days_remaining != 1 else ''}"

        # Create check-in
        checkin = CheckIn(
            client_id=checkin_data.client_id,
            method=CheckInMethod(checkin_data.method),
            station=checkin_data.station,
            notes=checkin_data.notes
        )

        db.add(checkin)
        await db.commit()
        await db.refresh(checkin)

        return CheckInResponse(
            id=str(checkin.id),
            client_id=str(checkin.client_id),
            method=checkin.method.value,
            station=checkin.station,
            happened_at=checkin.happened_at.isoformat(),
            notes=checkin.notes,
            created_at=checkin.created_at.isoformat(),
            client_first_name=client.first_name,
            client_last_name=client.last_name,
            membership_warning=membership_warning
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create check-in: {str(e)}")


@router.get("/stats", response_model=CheckInStats)
async def get_checkin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get check-in statistics"""
    try:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        # Total check-ins
        total_result = await db.execute(select(func.count(CheckIn.id)))
        total = total_result.scalar() or 0

        # Today's check-ins
        today_result = await db.execute(
            select(func.count(CheckIn.id)).where(CheckIn.happened_at >= today_start)
        )
        today = today_result.scalar() or 0

        # This week's check-ins
        week_result = await db.execute(
            select(func.count(CheckIn.id)).where(CheckIn.happened_at >= week_start)
        )
        this_week = week_result.scalar() or 0

        # This month's check-ins
        month_result = await db.execute(
            select(func.count(CheckIn.id)).where(CheckIn.happened_at >= month_start)
        )
        this_month = month_result.scalar() or 0

        return CheckInStats(
            today=today,
            this_week=this_week,
            this_month=this_month,
            total=total
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get check-in stats: {str(e)}")
