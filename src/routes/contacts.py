from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactResponse, ContactSchema, ContactUpdateSchema
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=List[ContactResponse],
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def get_contacts(
    limit: int = Query(default=10, ge=10, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> List[ContactResponse]:
    """
    The get_contacts function returns a list of contacts.
        The limit and offset parameters are used to paginate the results.


    :param limit: int: Limit the number of contacts returned
    :param ge: Check if the limit is greater than or equal to 10
    :param le: Limit the number of contacts returned
    :param offset: int: Determine how many contacts to skip
    :param ge: Set a minimum value for the limit parameter
    :param db: AsyncSession: Pass in the database session
    :param user: User: Get the current user from the auth_service
    :param : Limit the number of contacts returned
    :return: A list of contactresponse objects
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> ContactResponse:
    """
    The get_contact function returns a contact by id.
        The function takes in an integer as the contact_id, and returns a ContactResponse object.
        If no such contact exists, it raises an HTTPException with status code 404.

    :param contact_id: int: Get the contact id from the url path
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the database
    :param : Get the contact id from the url
    :return: A contactresponse object
    """
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail=f"Contact with id {contact_id} not found",
        )
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def create_contact(
    body: ContactSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> ContactResponse:
    """
    The create_contact function creates a new contact in the database.
        Args:
            body (ContactSchema): The contact to be created.
            db (AsyncSession): The database session to use for this request.
            user (User): The current user making the request, if any.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the repository layer
    :param user: User: Get the user who is making the request
    :param : Get the user from the database
    :return: A contactresponse
    """
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def update_contact(
    body: ContactUpdateSchema,
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> ContactResponse:
    """
    The update_contact function updates a contact in the database.
        It takes an id, body and db as parameters. The id is used to find the contact in the database,
        while the body contains all of the information that will be updated for that contact.
        The db parameter is used to connect to our PostgreSQL database.

    :param body: ContactUpdateSchema: Validate the request body
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Get the database session
    :param user: User: Get the user from the database
    :param : Get the id of the contact to be updated
    :return: A contactresponse, which is a pydantic model
    """
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail=f"Contact with id {contact_id} not found",
        )
    return contact


@router.delete(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def delete_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> ContactResponse:
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            db (AsyncSession): A database session object for interacting with the database.
            user (User): The current logged in user, used to verify that they are authorized to delete this resource.

    :param contact_id: int: Specify the contact id to be deleted
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user
    :param : Pass the id of the contact to be deleted
    :return: A contactresponse object, which is a pydantic model
    """
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail=f"Contact with id {contact_id} not found",
        )
    return contact


@router.get(
    "/search/",
    response_model=List[ContactResponse],
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def search_contacts(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> List[ContactResponse]:
    """
    The search_contacts function searches for contacts in the database.
        It takes three optional parameters: first_name, last_name, and email.
        If no parameters are provided, it returns all contacts.

    :param first_name: Optional[str]: Specify that the first_name parameter is optional
    :param last_name: Optional[str]: Search for contacts with a specific last name
    :param email: Optional[str]: Search for a contact by email
    :param db: AsyncSession: Pass the database session to the repository
    :param user: User: Get the current user
    :param : Get the current user
    :return: A list of contactresponse objects
    """
    contacts = await repositories_contacts.search_contacts(
        first_name, last_name, email, db, user
    )
    return contacts


@router.get(
    "/birthdays/",
    response_model=List[ContactResponse],
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def get_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
) -> List[ContactResponse]:
    """
    The get_birthdays function returns a list of contacts that have birthdays on the current day.


    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :param : Get the database connection
    :return: A list of contactresponse objects
    """
    contacts = await repositories_contacts.get_birthdays(db, user)
    return contacts
