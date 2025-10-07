"""
Check-ins API endpoints (stats and additional features)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import datetime, timedelta

from models import CheckIn
from core.database import AsyncSessionLocal
from auth_workaround import get_current_user, User

router = APIRouter(prefix="/checkins", tags=["Check-ins"])


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Schemas
class CheckInStats(BaseModel):
    today: int
    this_week: int
    this_month: int
    total: int


# Routes
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
