"""Seller Application related business logic service.

This module provides the SellerApplicationService class that encapsulates all operations related to seller applications, such as creating new applications, listing pending applications, retrieving application details, and reviewing applications (approving/rejecting).
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Sequence

from models import UserRole
from schema.seller_application import SellerApplicationStatus, SellerApplicationCreate, SellerApplicationResponse, SellerApplicationReview
from models.seller_application import SellerApplication
from services.user import UserService
from core.exceptions import BaseCustomException

logger = logging.getLogger(__name__)


class SellerApplicationService:
    def __init__(self, user_service: UserService, session: AsyncSession):
        self.user_service = user_service
        self.session = session

    async def create_application(self, request: SellerApplicationCreate) -> SellerApplicationResponse:
        """Creates a new seller application.

        Args:
            user_id (int): ID of the user applying for seller role
            details (str | None): Short justification for the application
            db (AsyncSession): Database session

        Raises:
            BaseCustomException: If user already has a pending application

        Returns:
            SellerApplication: The newly created seller application
        """
        stmt = select(SellerApplication).where(SellerApplication.user_id ==
                                               request.user_id, SellerApplication.status == SellerApplicationStatus.PENDING)
        result = await self.session.scalars(stmt)
        existing = result.first()

        if existing:
            logger.warning(
                f"User {request.user_id} attempted to create duplicate pending seller application")
            raise BaseCustomException(status_code=400, error="Duplicate application",
                                      description="There is already a pending seller application for this user")

        req = SellerApplication(
            user_id=request.user_id,
            details=request.details,
            status=SellerApplicationStatus.PENDING,
        )
        self.session.add(req)
        await self.session.commit()
        await self.session.refresh(req)
        logger.info(
            f"Seller application created: {req.id} by user {request.user_id}")
        return req

    async def list_applications(self, limit: int | None = None, offset: int | None = None) -> Sequence[SellerApplication]:
        """Lists all pending applications, with pagination.

        Args:
            limit (int | None, optional): Maximum number of applications to return. Defaults to None.
            offset (int | None, optional): Number of applications to skip. Defaults to None.

        Returns:
            Sequence[SellerApplication]: The list of seller applications
        """
        stmt = select(SellerApplication).where(SellerApplication.status == SellerApplicationStatus.PENDING).order_by(
            SellerApplication.created_at.desc())
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_application_by_id(self, application_id: int) -> SellerApplication:
        """Gets an application by its ID.

        Args:
            application_id (int): ID of the application to retrieve

        Returns:
            SellerApplication: The retrieved seller application
        """
        stmt = select(SellerApplication).where(
            SellerApplication.id == application_id)
        result = await self.session.scalars(stmt)
        return result.first()

    async def review_application(self,
                                 application_id: int,
                                 reviewer_id: int,
                                 review: SellerApplicationReview
                                 ) -> SellerApplication:
        """Updates a pending seller application, either approving or rejecting it.

        Args:
            application_id (int): ID of the application to review
            approve (bool): Whether to approve or reject the application
            reviewer_id (int): ID of the user reviewing the application
            admin_notes (str | None): Notes from the reviewer
            db (AsyncSession): Database session
        Raises:
            BaseCustomException: If application is not found
            BaseCustomException: If application is not pending
            BaseCustomException: If user promotion fails

        Returns:
            SellerApplication: The updated seller application
        """
        if review.status is SellerApplicationStatus.PENDING:
            raise BaseCustomException(status_code=400, error="Invalid review status",
                                      description="Review status must be either 'approved' or 'rejected'")

        stmt = select(SellerApplication).where(
            SellerApplication.id == application_id)
        result = await self.session.scalars(stmt)
        req = result.first()
        if not req:
            raise BaseCustomException(
                status_code=404, error="Not found", description="Seller application not found")

        if req.status != SellerApplicationStatus.PENDING:
            raise BaseCustomException(status_code=400, error="Already reviewed",
                                      description="Seller application has already been reviewed")

        req.reviewed_by = reviewer_id
        req.admin_notes = review.admin_notes
        req.reviewed_at = datetime.now(timezone.utc)
        req.status = SellerApplicationStatus.APPROVED if review.status == SellerApplicationStatus.APPROVED else SellerApplicationStatus.REJECTED

        if review.status == SellerApplicationStatus.APPROVED:
            _ = await self.user_service.update_user(req.user_id, role=UserRole.SELLER)

        await self.session.commit()
        await self.session.refresh(req)
        logger.info(
            f"Seller application {application_id} reviewed by {reviewer_id}: {'approved' if review.status == SellerApplicationStatus.APPROVED else 'rejected'}")
        return req
