from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from core.database import get_db
from core.exceptions import CRMException
from modules.core_auth.dependencies import require_staff
from .schemas import (
    MembershipCreate, MembershipUpdate, MembershipResponse,
    MembershipWithClientResponse, ExpiringMembershipsRequest,
    MembershipStatsResponse
)
from .service import MembershipService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Memberships"], dependencies=[Depends(require_staff)])


@router.post("/clients/{client_id}/membership", response_model=MembershipResponse, status_code=201)
async def create_membership(
    client_id: UUID,
    membership_data: MembershipCreate,
    db: AsyncSession = Depends(get_db)
) -> MembershipResponse:
    """Create a new membership for a client"""
    # Ensure client_id matches the URL parameter
    membership_data.client_id = client_id

    membership_service = MembershipService(db)

    try:
        membership = await membership_service.create_membership(membership_data)
        return MembershipResponse.from_orm(membership)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/clients/{client_id}/membership", response_model=Optional[MembershipResponse])
async def get_client_membership(
    client_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Optional[MembershipResponse]:
    """Get current membership for a client"""
    membership_service = MembershipService(db)

    membership = await membership_service.get_client_membership(client_id)
    if not membership:
        return None

    return MembershipResponse.from_orm(membership)


@router.get("/clients/{client_id}/memberships", response_model=List[MembershipResponse])
async def get_client_memberships(
    client_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> List[MembershipResponse]:
    """Get all memberships for a client"""
    membership_service = MembershipService(db)

    memberships = await membership_service.get_client_memberships(client_id)
    return [MembershipResponse.from_orm(membership) for membership in memberships]


@router.get("/memberships/{membership_id}", response_model=MembershipResponse)
async def get_membership(
    membership_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> MembershipResponse:
    """Get membership by ID"""
    membership_service = MembershipService(db)

    membership = await membership_service.get_membership_by_id(membership_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    return MembershipResponse.from_orm(membership)


@router.patch("/memberships/{membership_id}", response_model=MembershipResponse)
async def update_membership(
    membership_id: UUID,
    membership_data: MembershipUpdate,
    db: AsyncSession = Depends(get_db)
) -> MembershipResponse:
    """Update membership information"""
    membership_service = MembershipService(db)

    try:
        membership = await membership_service.update_membership(membership_id, membership_data)
        return MembershipResponse.from_orm(membership)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/memberships/{membership_id}")
async def delete_membership(
    membership_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete membership"""
    membership_service = MembershipService(db)

    try:
        await membership_service.delete_membership(membership_id)
        return {"message": "Membership deleted successfully"}
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/memberships/expiring", response_model=List[MembershipWithClientResponse])
async def get_expiring_memberships(
    days: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    plan_codes: Optional[List[str]] = Query(None, description="Filter by plan codes"),
    db: AsyncSession = Depends(get_db)
) -> List[MembershipWithClientResponse]:
    """Get memberships expiring within specified days"""
    membership_service = MembershipService(db)

    try:
        memberships = await membership_service.get_expiring_memberships(days, plan_codes)
        return [
            MembershipWithClientResponse(
                **membership.__dict__,
                client_name=membership.client.full_name,
                client_email=membership.client.email,
                client_phone=membership.client.phone
            )
            for membership in memberships
        ]
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/memberships/stats", response_model=MembershipStatsResponse)
async def get_membership_stats(
    db: AsyncSession = Depends(get_db)
) -> MembershipStatsResponse:
    """Get membership statistics"""
    membership_service = MembershipService(db)

    try:
        stats = await membership_service.get_membership_stats()
        return MembershipStatsResponse(**stats)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/memberships/by-status/{status}", response_model=List[MembershipWithClientResponse])
async def get_memberships_by_status(
    status: str,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db)
) -> List[MembershipWithClientResponse]:
    """Get memberships filtered by status (active, expired, pending)"""
    membership_service = MembershipService(db)

    try:
        memberships, total_count = await membership_service.get_memberships_by_status(status, limit, offset)
        # Note: In a real API, you'd typically return pagination metadata
        return [
            MembershipWithClientResponse(
                **membership.__dict__,
                client_name=membership.client.full_name,
                client_email=membership.client.email,
                client_phone=membership.client.phone
            )
            for membership in memberships
        ]
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)