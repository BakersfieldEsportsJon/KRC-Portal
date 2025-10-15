"""
Simplified clients API using central models
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging
import csv
import io

from models import Client, ContactMethod, Consent, Tag, Membership, CheckIn, CheckInMethod, ClientNote
from core.database import AsyncSessionLocal
from auth_workaround import get_current_user, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clients", tags=["Clients"])


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# RBAC dependency for admin-only operations
def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Schemas
class ClientCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)

    # POS/Service fields
    parent_guardian_name: Optional[str] = Field(None, max_length=200)
    pos_number: Optional[str] = Field(None, max_length=50)
    service_coordinator: Optional[str] = Field(None, max_length=200)
    pos_start_date: Optional[date] = None
    pos_end_date: Optional[date] = None
    notes: Optional[str] = None
    language: Optional[str] = Field(None, max_length=50)


class ClientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    parent_guardian_name: Optional[str] = Field(None, max_length=200)
    pos_number: Optional[str] = Field(None, max_length=50)
    service_coordinator: Optional[str] = Field(None, max_length=200)
    pos_start_date: Optional[date] = None
    pos_end_date: Optional[date] = None
    notes: Optional[str] = None
    language: Optional[str] = Field(None, max_length=50)


class POSExtensionUpdate(BaseModel):
    pos_end_date: date = Field(..., description="New POS end date")


class ClientResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    date_of_birth: Optional[date]
    email: Optional[str]
    phone: Optional[str]
    created_at: str

    # POS/Service fields
    parent_guardian_name: Optional[str] = None
    pos_number: Optional[str] = None
    service_coordinator: Optional[str] = None
    pos_start_date: Optional[date] = None
    pos_end_date: Optional[date] = None
    notes: Optional[str] = None
    language: Optional[str] = None

    # Membership info
    membership_status: Optional[str] = None  # 'active', 'expiring', 'expired', or None
    membership_end_date: Optional[date] = None
    membership_plan: Optional[str] = None

    class Config:
        from_attributes = True


class MembershipCreate(BaseModel):
    client_id: str
    plan_code: str = Field(..., max_length=50)
    starts_on: date
    ends_on: date
    notes: Optional[str] = None


class MembershipResponse(BaseModel):
    id: str
    client_id: str
    plan_code: str
    starts_on: date
    ends_on: date
    notes: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class CheckInCreate(BaseModel):
    client_id: str
    method: str = Field(default="staff", pattern="^(kiosk|staff)$")
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

    # Include client info for convenience
    client_first_name: Optional[str] = None
    client_last_name: Optional[str] = None

    # Membership status warning
    membership_warning: Optional[str] = None

    class Config:
        from_attributes = True


class MembershipStats(BaseModel):
    total: int
    active: int
    expiring_soon: int
    expired: int


class CheckInStats(BaseModel):
    today: int
    this_week: int
    this_month: int
    total: int


# Routes
@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new client (admin only)"""
    try:
        client = Client(
            first_name=client_data.first_name,
            last_name=client_data.last_name,
            date_of_birth=client_data.date_of_birth,
            email=client_data.email,
            phone=client_data.phone,
            parent_guardian_name=client_data.parent_guardian_name,
            pos_number=client_data.pos_number,
            service_coordinator=client_data.service_coordinator,
            pos_start_date=client_data.pos_start_date,
            pos_end_date=client_data.pos_end_date,
            notes=client_data.notes,
            language=client_data.language
        )

        db.add(client)
        await db.commit()
        await db.refresh(client)

        logger.info(f"Created client: {client.first_name} {client.last_name}")

        return ClientResponse(
            id=str(client.id),
            first_name=client.first_name,
            last_name=client.last_name,
            date_of_birth=client.date_of_birth,
            email=client.email,
            phone=client.phone,
            parent_guardian_name=client.parent_guardian_name,
            pos_number=client.pos_number,
            service_coordinator=client.service_coordinator,
            pos_start_date=client.pos_start_date,
            pos_end_date=client.pos_end_date,
            notes=client.notes,
            language=client.language,
            created_at=client.created_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create client")


@router.get("", response_model=List[ClientResponse])
async def list_clients(
    query: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List clients with optional search (name, email, phone, POS number) and membership status"""
    try:
        stmt = select(Client)

        if query:
            search_pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Client.first_name.ilike(search_pattern),
                    Client.last_name.ilike(search_pattern),
                    Client.email.ilike(search_pattern),
                    Client.phone.ilike(search_pattern),
                    Client.pos_number.ilike(search_pattern)
                )
            )

        stmt = stmt.limit(limit).offset(offset).order_by(Client.created_at.desc())

        result = await db.execute(stmt)
        clients = result.scalars().all()

        # Get membership info for each client
        today = date.today()
        expiring_threshold = today + timedelta(days=30)

        client_responses = []
        for c in clients:
            # Get active membership
            membership_stmt = select(Membership).where(
                Membership.client_id == c.id,
                Membership.ends_on >= today
            ).order_by(Membership.ends_on.desc())

            membership_result = await db.execute(membership_stmt)
            membership = membership_result.scalar_one_or_none()

            # Determine status
            status = None
            end_date = None
            plan = None

            if membership:
                end_date = membership.ends_on
                plan = membership.plan_code

                if membership.ends_on <= expiring_threshold:
                    status = "expiring"
                else:
                    status = "active"
            else:
                # Check if they have an expired membership
                expired_stmt = select(Membership).where(
                    Membership.client_id == c.id,
                    Membership.ends_on < today
                ).order_by(Membership.ends_on.desc())

                expired_result = await db.execute(expired_stmt)
                expired_membership = expired_result.scalar_one_or_none()

                if expired_membership:
                    status = "expired"
                    end_date = expired_membership.ends_on
                    plan = expired_membership.plan_code

            client_responses.append(ClientResponse(
                id=str(c.id),
                first_name=c.first_name,
                last_name=c.last_name,
                date_of_birth=c.date_of_birth,
                email=c.email,
                phone=c.phone,
                parent_guardian_name=c.parent_guardian_name,
                pos_number=c.pos_number,
                service_coordinator=c.service_coordinator,
                pos_start_date=c.pos_start_date,
                pos_end_date=c.pos_end_date,
                created_at=c.created_at.isoformat(),
                membership_status=status,
                membership_end_date=end_date,
                membership_plan=plan
            ))

        return client_responses
    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        raise HTTPException(status_code=500, detail="Failed to list clients")


@router.get("/import/template")
async def download_import_template(current_user: User = Depends(get_current_user)):
    """Download CSV template for bulk client import"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'first_name', 'last_name', 'email', 'phone', 'date_of_birth',
        'parent_guardian_name', 'pos_number', 'service_coordinator',
        'pos_start_date', 'pos_end_date'
    ])

    # Write example rows
    writer.writerow([
        'John', 'Doe', 'john.doe@example.com', '555-1234', '1990-01-15',
        'Jane Doe', 'POS-12345', 'Sarah Johnson', '2025-01-01', '2025-12-31'
    ])
    writer.writerow([
        'Jane', 'Smith', 'jane.smith@example.com', '555-5678', '1985-06-20',
        'Robert Smith', 'POS-67890', 'Mike Williams', '2025-02-01', '2026-01-31'
    ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=client_import_template.csv"}
    )


@router.post("/import")
async def import_clients(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Bulk import clients from CSV file (admin only)"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))

        created_count = 0
        errors = []

        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Parse dates if provided
                dob = None
                if row.get('date_of_birth'):
                    try:
                        dob = date.fromisoformat(row['date_of_birth'])
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid date format for date_of_birth")
                        continue

                pos_start = None
                if row.get('pos_start_date'):
                    try:
                        pos_start = date.fromisoformat(row['pos_start_date'])
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid date format for pos_start_date")
                        continue

                pos_end = None
                if row.get('pos_end_date'):
                    try:
                        pos_end = date.fromisoformat(row['pos_end_date'])
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid date format for pos_end_date")
                        continue

                client = Client(
                    first_name=row['first_name'].strip(),
                    last_name=row['last_name'].strip(),
                    email=row.get('email', '').strip() or None,
                    phone=row.get('phone', '').strip() or None,
                    date_of_birth=dob,
                    parent_guardian_name=row.get('parent_guardian_name', '').strip() or None,
                    pos_number=row.get('pos_number', '').strip() or None,
                    service_coordinator=row.get('service_coordinator', '').strip() or None,
                    pos_start_date=pos_start,
                    pos_end_date=pos_end
                )

                db.add(client)
                created_count += 1

            except KeyError as e:
                errors.append(f"Row {row_num}: Missing required field {e}")
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

        await db.commit()

        logger.info(f"Imported {created_count} clients")

        return {
            "success": True,
            "created_count": created_count,
            "errors": errors if errors else None
        }

    except Exception as e:
        logger.error(f"Error importing clients: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to import clients: {str(e)}")


@router.post("/checkins", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
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

        logger.info(f"Check-in created for client {client.first_name} {client.last_name}")

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
        logger.error(f"Error creating check-in: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create check-in")


@router.get("/checkins", response_model=List[CheckInResponse])
async def list_checkins(
    client_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List check-ins, optionally filtered by client"""
    try:
        stmt = select(CheckIn, Client).join(Client, CheckIn.client_id == Client.id)

        if client_id:
            stmt = stmt.where(CheckIn.client_id == client_id)

        stmt = stmt.order_by(CheckIn.happened_at.desc()).limit(limit).offset(offset)

        result = await db.execute(stmt)
        checkins_with_clients = result.all()

        return [
            CheckInResponse(
                id=str(checkin.id),
                client_id=str(checkin.client_id),
                method=checkin.method.value,
                station=checkin.station,
                happened_at=checkin.happened_at.isoformat(),
                notes=checkin.notes,
                created_at=checkin.created_at.isoformat(),
                client_first_name=client.first_name,
                client_last_name=client.last_name,
                membership_warning=None
            )
            for checkin, client in checkins_with_clients
        ]
    except Exception as e:
        logger.error(f"Error listing check-ins: {e}")
        raise HTTPException(status_code=500, detail="Failed to list check-ins")


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific client"""
    try:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        return ClientResponse(
            id=str(client.id),
            first_name=client.first_name,
            last_name=client.last_name,
            date_of_birth=client.date_of_birth,
            email=client.email,
            phone=client.phone,
            parent_guardian_name=client.parent_guardian_name,
            pos_number=client.pos_number,
            service_coordinator=client.service_coordinator,
            pos_start_date=client.pos_start_date,
            pos_end_date=client.pos_end_date,
            created_at=client.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client: {e}")
        raise HTTPException(status_code=500, detail="Failed to get client")


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a client (Admin: all fields, Staff: notes only)"""
    try:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # Role-based access control
        if current_user.role != "admin":
            # Staff can only update notes field
            non_notes_fields = {k: v for k, v in client_data.dict(exclude_unset=True).items() if k != 'notes'}
            if non_notes_fields:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Staff members can only update the notes field"
                )
            # Update only notes
            if client_data.notes is not None:
                client.notes = client_data.notes
        else:
            # Admin can update all fields
            if client_data.first_name is not None:
                client.first_name = client_data.first_name
            if client_data.last_name is not None:
                client.last_name = client_data.last_name
            if client_data.date_of_birth is not None:
                client.date_of_birth = client_data.date_of_birth
            if client_data.email is not None:
                client.email = client_data.email
            if client_data.phone is not None:
                client.phone = client_data.phone
            if client_data.parent_guardian_name is not None:
                client.parent_guardian_name = client_data.parent_guardian_name
            if client_data.pos_number is not None:
                client.pos_number = client_data.pos_number
            if client_data.service_coordinator is not None:
                client.service_coordinator = client_data.service_coordinator
            if client_data.pos_start_date is not None:
                client.pos_start_date = client_data.pos_start_date
            if client_data.pos_end_date is not None:
                client.pos_end_date = client_data.pos_end_date
            if client_data.notes is not None:
                client.notes = client_data.notes
            if client_data.language is not None:
                client.language = client_data.language

        await db.commit()
        await db.refresh(client)

        logger.info(f"Updated client {client.first_name} {client.last_name}")

        return ClientResponse(
            id=str(client.id),
            first_name=client.first_name,
            last_name=client.last_name,
            date_of_birth=client.date_of_birth,
            email=client.email,
            phone=client.phone,
            parent_guardian_name=client.parent_guardian_name,
            pos_number=client.pos_number,
            service_coordinator=client.service_coordinator,
            pos_start_date=client.pos_start_date,
            pos_end_date=client.pos_end_date,
            created_at=client.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update client")


@router.patch("/{client_id}/pos-extension", response_model=ClientResponse)
async def extend_pos_date(
    client_id: str,
    extension_data: POSExtensionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Extend POS end date for a client (admin only)"""
    try:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # Update POS end date
        client.pos_end_date = extension_data.pos_end_date
        await db.commit()
        await db.refresh(client)

        logger.info(f"Extended POS end date for client {client.first_name} {client.last_name} to {extension_data.pos_end_date}")

        return ClientResponse(
            id=str(client.id),
            first_name=client.first_name,
            last_name=client.last_name,
            date_of_birth=client.date_of_birth,
            email=client.email,
            phone=client.phone,
            parent_guardian_name=client.parent_guardian_name,
            pos_number=client.pos_number,
            service_coordinator=client.service_coordinator,
            pos_start_date=client.pos_start_date,
            pos_end_date=client.pos_end_date,
            created_at=client.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extending POS date: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to extend POS date")


@router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a client (admin only)"""
    try:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        await db.delete(client)
        await db.commit()

        logger.info(f"Deleted client {client.first_name} {client.last_name}")

        return {"message": "Client deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete client")


@router.post("/{client_id}/memberships", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
async def create_membership(
    client_id: str,
    membership_data: MembershipCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a membership for a client"""
    try:
        # Verify client exists
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        membership = Membership(
            client_id=client_id,
            plan_code=membership_data.plan_code,
            starts_on=membership_data.starts_on,
            ends_on=membership_data.ends_on,
            notes=membership_data.notes
        )

        db.add(membership)
        await db.commit()
        await db.refresh(membership)

        logger.info(f"Created membership for client {client_id}")

        return MembershipResponse(
            id=str(membership.id),
            client_id=str(membership.client_id),
            plan_code=membership.plan_code,
            starts_on=membership.starts_on,
            ends_on=membership.ends_on,
            notes=membership.notes,
            created_at=membership.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating membership: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create membership")


@router.get("/{client_id}/membership", response_model=MembershipResponse)
async def get_client_active_membership(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the active/current membership for a client"""
    try:
        today = date.today()
        stmt = select(Membership).where(
            Membership.client_id == client_id,
            Membership.ends_on >= today
        ).order_by(Membership.ends_on.desc())

        result = await db.execute(stmt)
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException(status_code=404, detail="No active membership found")

        return MembershipResponse(
            id=str(membership.id),
            client_id=str(membership.client_id),
            plan_code=membership.plan_code,
            starts_on=membership.starts_on,
            ends_on=membership.ends_on,
            notes=membership.notes,
            created_at=membership.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active membership: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active membership")


@router.get("/{client_id}/memberships", response_model=List[MembershipResponse])
async def list_client_memberships(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List memberships for a client"""
    try:
        stmt = select(Membership).where(Membership.client_id == client_id).order_by(Membership.starts_on.desc())
        result = await db.execute(stmt)
        memberships = result.scalars().all()

        return [
            MembershipResponse(
                id=str(m.id),
                client_id=str(m.client_id),
                plan_code=m.plan_code,
                starts_on=m.starts_on,
                ends_on=m.ends_on,
                notes=m.notes,
                created_at=m.created_at.isoformat()
            )
            for m in memberships
        ]
    except Exception as e:
        logger.error(f"Error listing memberships: {e}")
        raise HTTPException(status_code=500, detail="Failed to list memberships")


@router.get("/{client_id}/checkins", response_model=List[CheckInResponse])
async def list_client_checkins(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List check-ins for a specific client"""
    try:
        stmt = select(CheckIn, Client).join(Client, CheckIn.client_id == Client.id).where(
            CheckIn.client_id == client_id
        ).order_by(CheckIn.happened_at.desc())

        result = await db.execute(stmt)
        checkins_with_clients = result.all()

        return [
            CheckInResponse(
                id=str(checkin.id),
                client_id=str(checkin.client_id),
                method=checkin.method.value,
                station=checkin.station,
                happened_at=checkin.happened_at.isoformat(),
                notes=checkin.notes,
                created_at=checkin.created_at.isoformat(),
                client_first_name=client.first_name,
                client_last_name=client.last_name,
                membership_warning=None
            )
            for checkin, client in checkins_with_clients
        ]
    except Exception as e:
        logger.error(f"Error listing client check-ins: {e}")
        raise HTTPException(status_code=500, detail="Failed to list check-ins")


# Client Notes Schemas
class ClientNoteCreate(BaseModel):
    note: str = Field(..., min_length=1, max_length=5000)


class ClientNoteResponse(BaseModel):
    id: str
    client_id: str
    note: str
    created_at: str
    updated_at: str
    user_email: str
    user_id: str
    user_username: Optional[str] = None
    client_first_name: Optional[str] = None
    client_last_name: Optional[str] = None


# Client Notes Endpoints
@router.get("/{client_id}/notes", response_model=List[ClientNoteResponse])
async def get_client_notes(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notes for a client"""
    try:
        # Verify client exists
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # Get notes with user info
        notes_result = await db.execute(
            select(ClientNote, User)
            .join(User, ClientNote.user_id == User.id)
            .where(ClientNote.client_id == client_id)
            .order_by(ClientNote.created_at.desc())
        )
        notes_with_users = notes_result.all()

        return [
            ClientNoteResponse(
                id=str(note.id),
                client_id=str(note.client_id),
                note=note.note,
                created_at=note.created_at.isoformat(),
                updated_at=note.updated_at.isoformat(),
                user_email=user.email,
                user_id=str(user.id),
                user_username=user.username
            )
            for note, user in notes_with_users
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get client notes")


@router.post("/{client_id}/notes", response_model=ClientNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_client_note(
    client_id: str,
    note_data: ClientNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new note for a client"""
    try:
        # Verify client exists
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # Create note
        note = ClientNote(
            client_id=client_id,
            user_id=current_user.id,
            note=note_data.note
        )

        db.add(note)
        await db.commit()
        await db.refresh(note)

        return ClientNoteResponse(
            id=str(note.id),
            client_id=str(note.client_id),
            note=note.note,
            created_at=note.created_at.isoformat(),
            updated_at=note.updated_at.isoformat(),
            user_email=current_user.email,
            user_id=str(current_user.id),
            user_username=current_user.username
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client note: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create client note")


@router.get("/notes/recent", response_model=List[ClientNoteResponse])
async def get_recent_notes(
    days: int = 7,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent notes from the past N days across all clients"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)

        # Get notes with user and client info - explicitly specify join order
        notes_result = await db.execute(
            select(ClientNote, User, Client)
            .select_from(ClientNote)
            .join(User, ClientNote.user_id == User.id)
            .join(Client, ClientNote.client_id == Client.id)
            .where(ClientNote.created_at >= cutoff_date)
            .order_by(ClientNote.created_at.desc())
            .limit(limit)
        )
        notes_with_info = notes_result.all()

        return [
            ClientNoteResponse(
                id=str(note.id),
                client_id=str(note.client_id),
                note=note.note,
                created_at=note.created_at.isoformat(),
                updated_at=note.updated_at.isoformat(),
                user_email=user.email,
                user_id=str(user.id),
                user_username=user.username,
                client_first_name=client.first_name,
                client_last_name=client.last_name
            )
            for note, user, client in notes_with_info
        ]
    except Exception as e:
        logger.error(f"Error getting recent notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recent notes")
