from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from core.database import get_db
from core.exceptions import CRMException
from modules.core_auth.dependencies import require_staff, require_admin_role, get_current_active_user
from modules.core_auth.models import User
from .schemas import (
    ClientCreate, ClientUpdate, ClientResponse, ClientListResponse,
    TagResponse, ContactMethodCreate, ContactMethodResponse,
    AddTagRequest, AddConsentRequest, ClientSearchRequest
)
from .service import ClientService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Clients"], dependencies=[Depends(require_staff)])


@router.post("/clients", response_model=ClientResponse, status_code=201)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
) -> ClientResponse:
    """Create a new client (Admin only)"""
    client_service = ClientService(db)

    try:
        client = await client_service.create_client(client_data)
        return ClientResponse.from_orm(client)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/clients", response_model=List[ClientListResponse])
async def search_clients(
    query: Optional[str] = Query(None, description="Search query for name, email, or phone"),
    tags: Optional[List[str]] = Query(None, description="Filter by tag names"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db)
) -> List[ClientListResponse]:
    """Search clients with optional filters"""
    client_service = ClientService(db)

    try:
        clients, total_count = await client_service.search_clients(query, tags, limit, offset)
        # Note: In a real API, you'd typically return pagination metadata
        return [ClientListResponse.from_orm(client) for client in clients]
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ClientResponse:
    """Get client by ID"""
    client_service = ClientService(db)

    client = await client_service.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return ClientResponse.from_orm(client)


@router.patch("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ClientResponse:
    """Update client information (Admin: all fields, Staff: notes only)"""
    client_service = ClientService(db)

    try:
        # Staff can only update notes field
        if not current_user.is_admin:
            # Create a new ClientUpdate with only notes field
            allowed_data = ClientUpdate(notes=client_data.notes)
            # Set all other fields to None explicitly
            for field in client_data.dict(exclude={'notes'}, exclude_unset=True):
                if client_data.dict()[field] is not None:
                    raise HTTPException(
                        status_code=403,
                        detail="Staff members can only update the notes field"
                    )
            client = await client_service.update_client(client_id, allowed_data)
        else:
            client = await client_service.update_client(client_id, client_data)

        return ClientResponse.from_orm(client)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """Delete client (Admin only)"""
    client_service = ClientService(db)

    try:
        await client_service.delete_client(client_id)
        return {"message": "Client deleted successfully"}
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/clients/{client_id}/tags", response_model=ClientResponse)
async def add_tags_to_client(
    client_id: UUID,
    tag_data: AddTagRequest,
    db: AsyncSession = Depends(get_db)
) -> ClientResponse:
    """Add tags to client"""
    client_service = ClientService(db)

    try:
        client = await client_service.add_tags_to_client(client_id, tag_data.tag_names)
        return ClientResponse.from_orm(client)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/clients/{client_id}/tags/{tag_name}", response_model=ClientResponse)
async def remove_tag_from_client(
    client_id: UUID,
    tag_name: str,
    db: AsyncSession = Depends(get_db)
) -> ClientResponse:
    """Remove tag from client"""
    client_service = ClientService(db)

    try:
        client = await client_service.remove_tag_from_client(client_id, tag_name)
        return ClientResponse.from_orm(client)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/clients/{client_id}/contact-methods", response_model=ContactMethodResponse)
async def add_contact_method(
    client_id: UUID,
    contact_data: ContactMethodCreate,
    db: AsyncSession = Depends(get_db)
) -> ContactMethodResponse:
    """Add contact method to client"""
    client_service = ClientService(db)

    try:
        contact_method = await client_service.add_contact_method(client_id, contact_data)
        return ContactMethodResponse.from_orm(contact_method)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/clients/{client_id}/consents")
async def add_consents(
    client_id: UUID,
    consent_data: AddConsentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Add consents to client"""
    client_service = ClientService(db)

    try:
        consents = await client_service.add_consents(client_id, consent_data.consents)
        return {"message": f"Added {len(consents)} consents to client"}
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/tags", response_model=List[TagResponse])
async def get_all_tags(
    db: AsyncSession = Depends(get_db)
) -> List[TagResponse]:
    """Get all available tags"""
    client_service = ClientService(db)

    try:
        tags = await client_service.get_all_tags()
        return [TagResponse.from_orm(tag) for tag in tags]
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)