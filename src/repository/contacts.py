from datetime import date, timedelta
from typing import Optional

from sqlalchemy import and_, extract, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_contacts function returns a list of contacts for the user.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the offset of the query
    :param db: AsyncSession: Pass the database session to this function
    :param user: User: Filter the contacts by user
    :return: A list of contact objects
    """

    stmt = select(Contact).filter_by(user_id=user.id).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The get_contact function returns a contact from the database.

    :param contact_id: int: Get the contact with that id from the database
    :param db: AsyncSession: Pass in the database session
    :param user: User: Check if the user is allowed to access this contact
    :return: A contact object
    """
    stmt = select(Contact).filter_by(id=contact_id, user_id=user.id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the body of the request
    :param db: AsyncSession: Access the database
    :param user: User: Get the user id from the user object
    :return: A contact object
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User
):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Get the contact that needs to be updated
    :param body: ContactUpdateSchema: Validate the data sent in the request body
    :param db: AsyncSession: Pass in a database session to the function
    :param user: User: Get the user id from the token
    :return: A contact object or none
    """
    stmt = select(Contact).filter_by(id=contact_id, user_id=user.id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        contact.additional_info = body.additional_info
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Ensure that the user is only deleting their own contacts
    :return: The contact that was deleted
    """
    stmt = select(Contact).filter_by(id=contact_id, user_id=user.id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if contact is None:
        return None

    await db.delete(contact)
    await db.commit()
    return contact


async def search_contacts(
    first_name: Optional[str],
    last_name: Optional[str],
    email: Optional[str],
    db: AsyncSession,
    user: User,
):
    """
    The search_contacts function searches for contacts in the database.

    :param first_name: Optional[str]: Specify the type of data that will be passed to the function
    :param last_name: Optional[str]: Search for a contact by last name
    :param email: Optional[str]: Search for a contact by email
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the contacts by user
    :param : Pass the database session to the function
    :return: A list of contact objects
    """
    query = select(Contact).filter_by(user_id=user.id)

    filters = []
    if first_name:
        filters.append(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        filters.append(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        filters.append(Contact.email.ilike(f"%{email}%"))

    if filters:
        query = query.filter(or_(*filters))

    result = await db.execute(query)
    return result.scalars().all()


async def get_birthdays(db: AsyncSession, user: User):
    """
    The get_birthdays function returns a list of contacts that have birthdays in the next 7 days.

    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user's id
    :return: A list of birthdays
    """
    today = date.today()
    upcoming_date = today + timedelta(days=7)

    query = select(Contact).filter(
        Contact.user_id == user.id,
        or_(
            and_(
                extract("month", Contact.birthday) == today.month,
                extract("day", Contact.birthday) >= today.day,
            ),
            and_(
                extract("month", Contact.birthday) == upcoming_date.month,
                extract("day", Contact.birthday) <= upcoming_date.day,
            ),
        ),
    )

    result = await db.execute(query)
    return result.scalars().all()
