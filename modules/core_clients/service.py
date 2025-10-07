from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Tuple
from uuid import UUID
from core.exceptions import NotFoundError, ValidationError, DuplicateError
from .models import Client, Tag, ContactMethod, Consent, client_tags
from .schemas import ClientCreate, ClientUpdate, TagCreate, ContactMethodCreate, ConsentCreate
import logging

logger = logging.getLogger(__name__)


class ClientService:
    """Client management service"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_client(self, client_data: ClientCreate) -> Client:
        """Create a new client"""
        # Check for duplicate email or phone if provided
        if client_data.email or client_data.phone:
            conditions = []
            if client_data.email:
                conditions.append(Client.email == client_data.email)
            if client_data.phone:
                conditions.append(Client.phone == client_data.phone)

            stmt = select(Client).where(or_(*conditions))
            result = await self.db.execute(stmt)
            existing_client = result.scalar_one_or_none()

            if existing_client:
                if existing_client.email == client_data.email:
                    raise DuplicateError("Client", "email")
                if existing_client.phone == client_data.phone:
                    raise DuplicateError("Client", "phone")

        # Create client
        client = Client(
            first_name=client_data.first_name,
            last_name=client_data.last_name,
            date_of_birth=client_data.date_of_birth,
            email=client_data.email,
            phone=client_data.phone,
            external_ids=client_data.external_ids
        )

        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)
        logger.info(f"Created client: {client.full_name}")
        return client

    async def get_client_by_id(self, client_id: UUID) -> Optional[Client]:
        """Get client by ID with related data"""
        stmt = select(Client).options(
            selectinload(Client.tags),
            selectinload(Client.contact_methods),
            selectinload(Client.consents),
            selectinload(Client.memberships),
        ).where(Client.id == client_id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_clients(self, query: Optional[str] = None, tag_names: Optional[List[str]] = None,
                           limit: int = 50, offset: int = 0) -> Tuple[List[Client], int]:
        """Search clients with optional filters"""
        # Base query
        stmt = select(Client)
        count_stmt = select(func.count(Client.id))

        conditions = []

        # Text search in name, email, phone
        if query:
            search_term = f"%{query.lower()}%"
            text_conditions = [
                func.lower(Client.first_name).like(search_term),
                func.lower(Client.last_name).like(search_term),
                func.lower(func.concat(Client.first_name, ' ', Client.last_name)).like(search_term)
            ]
            if '@' in query:  # Likely an email search
                text_conditions.append(func.lower(Client.email).like(search_term))
            elif query.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').isdigit():
                # Likely a phone search
                text_conditions.append(Client.phone.like(f"%{query}%"))

            conditions.append(or_(*text_conditions))

        # Tag filter
        if tag_names:
            stmt = stmt.join(client_tags).join(Tag)
            count_stmt = count_stmt.join(client_tags).join(Tag)
            conditions.append(Tag.name.in_(tag_names))

        # Apply conditions
        if conditions:
            where_clause = and_(*conditions)
            stmt = stmt.where(where_clause)
            count_stmt = count_stmt.where(where_clause)

        # Get total count
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar()

        # Apply pagination and ordering
        stmt = stmt.order_by(Client.created_at.desc()).limit(limit).offset(offset)

        # Execute query
        result = await self.db.execute(stmt)
        clients = result.scalars().all()

        return list(clients), total_count

    async def update_client(self, client_id: UUID, client_data: ClientUpdate) -> Client:
        """Update client information"""
        client = await self.get_client_by_id(client_id)
        if not client:
            raise NotFoundError("Client", str(client_id))

        # Check for duplicate email or phone if being updated
        if client_data.email or client_data.phone:
            conditions = []
            if client_data.email and client_data.email != client.email:
                conditions.append(Client.email == client_data.email)
            if client_data.phone and client_data.phone != client.phone:
                conditions.append(Client.phone == client_data.phone)

            if conditions:
                conditions.append(Client.id != client_id)
                stmt = select(Client).where(and_(or_(*conditions[:-1]), conditions[-1]))
                result = await self.db.execute(stmt)
                existing_client = result.scalar_one_or_none()

                if existing_client:
                    if existing_client.email == client_data.email:
                        raise DuplicateError("Client", "email")
                    if existing_client.phone == client_data.phone:
                        raise DuplicateError("Client", "phone")

        # Update fields
        update_data = client_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)

        await self.db.commit()
        await self.db.refresh(client)
        logger.info(f"Updated client: {client.full_name}")
        return client

    async def delete_client(self, client_id: UUID) -> bool:
        """Delete client and related data"""
        client = await self.get_client_by_id(client_id)
        if not client:
            raise NotFoundError("Client", str(client_id))

        await self.db.delete(client)
        await self.db.commit()
        logger.info(f"Deleted client: {client.full_name}")
        return True

    async def get_or_create_tag(self, tag_name: str) -> Tag:
        """Get existing tag or create new one"""
        stmt = select(Tag).where(Tag.name == tag_name)
        result = await self.db.execute(stmt)
        tag = result.scalar_one_or_none()

        if not tag:
            tag = Tag(name=tag_name)
            self.db.add(tag)
            await self.db.commit()
            await self.db.refresh(tag)
            logger.info(f"Created new tag: {tag_name}")

        return tag

    async def add_tags_to_client(self, client_id: UUID, tag_names: List[str]) -> Client:
        """Add tags to client"""
        client = await self.get_client_by_id(client_id)
        if not client:
            raise NotFoundError("Client", str(client_id))

        for tag_name in tag_names:
            tag = await self.get_or_create_tag(tag_name)
            if tag not in client.tags:
                client.tags.append(tag)

        await self.db.commit()
        await self.db.refresh(client)
        logger.info(f"Added tags {tag_names} to client: {client.full_name}")
        return client

    async def remove_tag_from_client(self, client_id: UUID, tag_name: str) -> Client:
        """Remove tag from client"""
        client = await self.get_client_by_id(client_id)
        if not client:
            raise NotFoundError("Client", str(client_id))

        tag_to_remove = None
        for tag in client.tags:
            if tag.name == tag_name:
                tag_to_remove = tag
                break

        if tag_to_remove:
            client.tags.remove(tag_to_remove)
            await self.db.commit()
            await self.db.refresh(client)
            logger.info(f"Removed tag {tag_name} from client: {client.full_name}")

        return client

    async def add_contact_method(self, client_id: UUID, contact_data: ContactMethodCreate) -> ContactMethod:
        """Add contact method to client"""
        client = await self.get_client_by_id(client_id)
        if not client:
            raise NotFoundError("Client", str(client_id))

        contact_method = ContactMethod(
            client_id=client_id,
            type=contact_data.type,
            value=contact_data.value,
            verified=contact_data.verified
        )

        self.db.add(contact_method)
        await self.db.commit()
        await self.db.refresh(contact_method)
        logger.info(f"Added contact method {contact_data.type} to client: {client.full_name}")
        return contact_method

    async def add_consents(self, client_id: UUID, consents_data: List[ConsentCreate]) -> List[Consent]:
        """Add consents to client"""
        client = await self.get_client_by_id(client_id)
        if not client:
            raise NotFoundError("Client", str(client_id))

        consents = []
        for consent_data in consents_data:
            consent = Consent(
                client_id=client_id,
                kind=consent_data.kind,
                granted=consent_data.granted,
                granted_at=func.now() if consent_data.granted else None,
                source=consent_data.source
            )
            self.db.add(consent)
            consents.append(consent)

        await self.db.commit()
        for consent in consents:
            await self.db.refresh(consent)

        logger.info(f"Added {len(consents)} consents to client: {client.full_name}")
        return consents

    async def get_all_tags(self) -> List[Tag]:
        """Get all available tags"""
        stmt = select(Tag).order_by(Tag.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())