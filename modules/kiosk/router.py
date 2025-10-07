from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date
from core.database import get_db
from core.exceptions import CRMException
from modules.core_auth.dependencies import require_staff, get_current_user_optional
from .schemas import (
    CheckInCreate, KioskCheckInRequest, CheckInResponse,
    CheckInListResponse, ClientLookupResponse, CheckInStatsResponse
)
from .service import KioskService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Check-ins"])


# Public kiosk endpoints (no authentication required)
@router.post("/checkins/kiosk", response_model=CheckInResponse, status_code=201)
async def kiosk_checkin(
    checkin_data: KioskCheckInRequest,
    db: AsyncSession = Depends(get_db)
) -> CheckInResponse:
    """Self-service kiosk check-in (no authentication required)"""
    kiosk_service = KioskService(db)

    try:
        checkin = await kiosk_service.kiosk_checkin(checkin_data)
        client_info = await kiosk_service.get_client_with_membership_status(checkin.client_id)

        return CheckInResponse(
            **checkin.__dict__,
            client_name=client_info["full_name"],
            client_email=client_info["email"],
            client_phone=client_info["phone"]
        )
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/checkins/lookup", response_model=Optional[ClientLookupResponse])
async def lookup_client(
    phone: Optional[str] = Query(None, description="Client phone number"),
    code: Optional[str] = Query(None, description="Client lookup code"),
    db: AsyncSession = Depends(get_db)
) -> Optional[ClientLookupResponse]:
    """Look up client for kiosk check-in (no authentication required)"""
    if not phone and not code:
        raise HTTPException(status_code=400, detail="Must provide phone or code")

    kiosk_service = KioskService(db)

    try:
        client = await kiosk_service.lookup_client(phone, code)
        if not client:
            return None

        client_info = await kiosk_service.get_client_with_membership_status(client.id)
        return ClientLookupResponse(**client_info)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# Staff endpoints (authentication required)
@router.post("/checkins", response_model=CheckInResponse, status_code=201, dependencies=[Depends(require_staff)])
async def create_checkin(
    checkin_data: CheckInCreate,
    db: AsyncSession = Depends(get_db)
) -> CheckInResponse:
    """Create a new check-in (staff only)"""
    kiosk_service = KioskService(db)

    try:
        checkin = await kiosk_service.create_checkin(checkin_data)
        client_info = await kiosk_service.get_client_with_membership_status(checkin.client_id)

        return CheckInResponse(
            **checkin.__dict__,
            client_name=client_info["full_name"],
            client_email=client_info["email"],
            client_phone=client_info["phone"]
        )
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/checkins", response_model=List[CheckInListResponse], dependencies=[Depends(require_staff)])
async def get_recent_checkins(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db)
) -> List[CheckInListResponse]:
    """Get recent check-ins (staff only)"""
    kiosk_service = KioskService(db)

    try:
        checkins = await kiosk_service.get_recent_checkins(limit, offset)
        return [
            CheckInListResponse(
                **checkin.__dict__,
                client_name=checkin.client.full_name
            )
            for checkin in checkins
        ]
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/checkins/{checkin_id}", response_model=CheckInResponse, dependencies=[Depends(require_staff)])
async def get_checkin(
    checkin_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> CheckInResponse:
    """Get check-in by ID (staff only)"""
    kiosk_service = KioskService(db)

    checkin = await kiosk_service.get_checkin_by_id(checkin_id)
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")

    return CheckInResponse(
        **checkin.__dict__,
        client_name=checkin.client.full_name,
        client_email=checkin.client.email,
        client_phone=checkin.client.phone
    )


@router.get("/clients/{client_id}/checkins", response_model=List[CheckInListResponse], dependencies=[Depends(require_staff)])
async def get_client_checkins(
    client_id: UUID,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db)
) -> List[CheckInListResponse]:
    """Get check-ins for a specific client (staff only)"""
    kiosk_service = KioskService(db)

    try:
        checkins = await kiosk_service.get_client_checkins(client_id, limit, offset)
        return [
            CheckInListResponse(
                **checkin.__dict__,
                client_name=checkin.client.full_name
            )
            for checkin in checkins
        ]
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/checkins/date-range/{start_date}/{end_date}", response_model=List[CheckInListResponse], dependencies=[Depends(require_staff)])
async def get_checkins_by_date_range(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db)
) -> List[CheckInListResponse]:
    """Get check-ins within a date range (staff only)"""
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    kiosk_service = KioskService(db)

    try:
        checkins = await kiosk_service.get_checkins_by_date_range(start_date, end_date)
        return [
            CheckInListResponse(
                **checkin.__dict__,
                client_name=checkin.client.full_name
            )
            for checkin in checkins
        ]
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/checkins/stats", response_model=CheckInStatsResponse, dependencies=[Depends(require_staff)])
async def get_checkin_stats(
    db: AsyncSession = Depends(get_db)
) -> CheckInStatsResponse:
    """Get check-in statistics (staff only)"""
    kiosk_service = KioskService(db)

    try:
        stats = await kiosk_service.get_checkin_stats()
        return CheckInStatsResponse(**stats)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)