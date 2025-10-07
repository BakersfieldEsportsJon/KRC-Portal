from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Dict, Tuple
from uuid import UUID
from datetime import datetime, date, timedelta
from core.exceptions import NotFoundError, ValidationError
from .models import CheckIn, CheckInMethod
from modules.core_clients.models import Client
from modules.memberships.models import Membership
from .schemas import CheckInCreate, KioskCheckInRequest
import logging

logger = logging.getLogger(__name__)


class KioskService:
    """Kiosk and check-in management service"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def lookup_client(self, phone: Optional[str] = None, code: Optional[str] = None) -> Optional[Client]:
        """Look up client by phone or code"""
        if not phone and not code:
            return None

        conditions = []
        if phone:
            # Clean phone number for lookup
            cleaned_phone = phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('+1', '')
            # Try both formatted and unformatted versions
            conditions.extend([
                Client.phone == phone,
                Client.phone.like(f"%{cleaned_phone}%")
            ])

        if code:
            # Code could be stored in external_ids or other fields
            conditions.extend([
                Client.external_ids.op('->>')('code') == code,
                Client.external_ids.op('->>')('member_id') == code,
                func.cast(Client.id, func.VARCHAR).like(f"{code}%")  # Partial UUID match
            ])

        stmt = select(Client).where(or_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_checkin(self, checkin_data: CheckInCreate) -> CheckIn:
        """Create a new check-in"""
        # Validate that we have a way to identify the client
        checkin_data.validate_client_identifier()

        client = None

        # Find client by the provided identifier
        if checkin_data.client_id:
            stmt = select(Client).where(Client.id == checkin_data.client_id)
            result = await self.db.execute(stmt)
            client = result.scalar_one_or_none()
        else:
            client = await self.lookup_client(checkin_data.phone, checkin_data.code)

        if not client:
            raise NotFoundError("Client", "with provided identifier")

        # Create check-in
        checkin = CheckIn(
            client_id=client.id,
            method=checkin_data.method,
            station=checkin_data.station,
            notes=checkin_data.notes,
            happened_at=datetime.utcnow()
        )

        self.db.add(checkin)
        await self.db.commit()
        await self.db.refresh(checkin)
        logger.info(f"Created check-in for client {client.full_name} at station {checkin_data.station}")
        return checkin

    async def kiosk_checkin(self, checkin_data: KioskCheckInRequest) -> CheckIn:
        """Process kiosk check-in"""
        checkin_data.validate_identifier()

        # Look up client
        client = await self.lookup_client(checkin_data.phone, checkin_data.code)
        if not client:
            raise NotFoundError("Client", "with provided information")

        # Create check-in with kiosk method
        checkin_create = CheckInCreate(
            client_id=client.id,
            method=CheckInMethod.KIOSK,
            station=checkin_data.station,
            notes="Kiosk self-service check-in"
        )

        return await self.create_checkin(checkin_create)

    async def get_checkin_by_id(self, checkin_id: UUID) -> Optional[CheckIn]:
        """Get check-in by ID"""
        stmt = select(CheckIn).options(
            joinedload(CheckIn.client)
        ).where(CheckIn.id == checkin_id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_client_checkins(self, client_id: UUID, limit: int = 50, offset: int = 0) -> List[CheckIn]:
        """Get check-ins for a specific client"""
        stmt = select(CheckIn).options(
            joinedload(CheckIn.client)
        ).where(CheckIn.client_id == client_id).order_by(
            CheckIn.happened_at.desc()
        ).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_checkins(self, limit: int = 100, offset: int = 0) -> List[CheckIn]:
        """Get recent check-ins across all clients"""
        stmt = select(CheckIn).options(
            joinedload(CheckIn.client)
        ).order_by(CheckIn.happened_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_checkins_by_date_range(self, start_date: date, end_date: date) -> List[CheckIn]:
        """Get check-ins within a date range"""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        stmt = select(CheckIn).options(
            joinedload(CheckIn.client)
        ).where(
            and_(
                CheckIn.happened_at >= start_datetime,
                CheckIn.happened_at <= end_datetime
            )
        ).order_by(CheckIn.happened_at.desc())

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_checkin_stats(self) -> Dict:
        """Get check-in statistics"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        # Today's check-ins
        today_count = await self.db.scalar(
            select(func.count(CheckIn.id)).where(
                func.date(CheckIn.happened_at) == today
            )
        )

        # This week's check-ins
        week_count = await self.db.scalar(
            select(func.count(CheckIn.id)).where(
                CheckIn.happened_at >= datetime.combine(week_start, datetime.min.time())
            )
        )

        # This month's check-ins
        month_count = await self.db.scalar(
            select(func.count(CheckIn.id)).where(
                CheckIn.happened_at >= datetime.combine(month_start, datetime.min.time())
            )
        )

        # Unique clients today
        unique_today = await self.db.scalar(
            select(func.count(func.distinct(CheckIn.client_id))).where(
                func.date(CheckIn.happened_at) == today
            )
        )

        # Unique clients this week
        unique_week = await self.db.scalar(
            select(func.count(func.distinct(CheckIn.client_id))).where(
                CheckIn.happened_at >= datetime.combine(week_start, datetime.min.time())
            )
        )

        # Unique clients this month
        unique_month = await self.db.scalar(
            select(func.count(func.distinct(CheckIn.client_id))).where(
                CheckIn.happened_at >= datetime.combine(month_start, datetime.min.time())
            )
        )

        # Popular stations this month
        station_stats = await self.db.execute(
            select(
                CheckIn.station,
                func.count(CheckIn.id).label('count')
            ).where(
                and_(
                    CheckIn.happened_at >= datetime.combine(month_start, datetime.min.time()),
                    CheckIn.station.isnot(None)
                )
            ).group_by(CheckIn.station).order_by(func.count(CheckIn.id).desc()).limit(10)
        )

        popular_stations = {row.station: row.count for row in station_stats}

        return {
            "today": today_count or 0,
            "this_week": week_count or 0,
            "this_month": month_count or 0,
            "unique_clients_today": unique_today or 0,
            "unique_clients_week": unique_week or 0,
            "unique_clients_month": unique_month or 0,
            "popular_stations": popular_stations
        }

    async def get_client_with_membership_status(self, client_id: UUID) -> Optional[Dict]:
        """Get client information with current membership status"""
        # Get client
        stmt = select(Client).where(Client.id == client_id)
        result = await self.db.execute(stmt)
        client = result.scalar_one_or_none()

        if not client:
            return None

        # Get current membership
        membership_stmt = select(Membership).where(
            Membership.client_id == client_id
        ).order_by(Membership.created_at.desc())

        membership_result = await self.db.execute(membership_stmt)
        membership = membership_result.scalar_one_or_none()

        return {
            "id": client.id,
            "full_name": client.full_name,
            "email": client.email,
            "phone": client.phone,
            "membership_status": membership.status if membership else None,
            "membership_expires": membership.ends_on.isoformat() if membership else None
        }