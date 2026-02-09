"""Seller Application Routes"""

from fastapi import APIRouter, Depends, status

from core.dependencies import get_seller_application_service, require_role
from models.user import User, UserRole
from schema.seller_application import SellerApplicationCreate, SellerApplicationResponse, SellerApplicationReview, SellerApplicationShow
from services.seller_application import SellerApplicationService

router = APIRouter(
    prefix="/seller-applications",
    tags=["seller-applications"],
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
    }
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SellerApplicationResponse,
    summary="Submit seller role request",
)
async def submit_seller_request(
    request: SellerApplicationCreate,
    current_user: User = Depends(require_role(UserRole.BUYER)),
    seller_application_service: SellerApplicationService = Depends(
        get_seller_application_service),
) -> SellerApplicationResponse:
    """Create a new seller application for the current user.

    Args:
        request (SellerApplicationCreate): Request body containing application details
        current_user (User, optional): Dependency that checks the current user's role and returns their details. Defaults to Depends(require_role(UserRole.BUYER)).
        seller_application_service (SellerApplicationService, optional): SellerApplicationService dependency. Defaults to Depends( get_seller_application_service).

    Returns:
        SellerApplicationResponse: Response body from the created application
    """
    request = SellerApplicationCreate(current_user.id, request.details)
    application = seller_application_service.create_application(request)
    return application


@router.get(
    "/",
    response_model=list[SellerApplicationShow],
    summary="List all seller applications (admin)",
)
async def list_seller_applications(
    seller_application_service: SellerApplicationService = Depends(
        get_seller_application_service),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> list[SellerApplicationShow]:
    """Lists seller applications. Can only be accessed by admins.

    Args:
        seller_application_service (SellerApplicationService, optional): SellerApplicationService dependency. Defaults to Depends( get_seller_application_service).
        _ (User, optional): Dependency that checks the current user's role and returns their details. User details are not needed. Defaults to Depends(require_role(UserRole.ADMIN)).

    Returns:
        list[SellerApplicationShow]: List of seller applications with user details
    """
    reqs = await seller_application_service.list_applications()
    return reqs


@router.post(
    "/{application_id}/review",
    response_model=SellerApplicationResponse,
    summary="Review a seller application",
)
async def review_seller_request(
    application_id: int,
    review: SellerApplicationReview,
    seller_application_service: SellerApplicationService = Depends(
        get_seller_application_service),
    admin_user: User = Depends(require_role(UserRole.ADMIN)),
) -> SellerApplicationResponse:
    """Submit a review for a seller application. Only admins can access this endpoint. Approving an application promotes the user to SELLER role, while rejecting keeps them as BUYER.

    Args:
        application_id (int): Application ID to review
        review (SellerApplicationReview): Review details including status and admin notes
        seller_application_service (SellerApplicationService, optional): SellerApplicationService dependency. Defaults to Depends( get_seller_application_service).
        admin_user (User, optional): Admin user details. Defaults to Depends(require_role(UserRole.ADMIN)).

    Returns:
        SellerApplicationResponse: _description_
    """
    application = await seller_application_service.review_application(application_id, admin_user.id, review)
    return application
