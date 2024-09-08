from sqlalchemy.orm import Session
from . import models

def find_contact_by_email_or_phone(db: Session, email: str = None, phone: str = None):
    contacts = []
    query = db.query(models.Contact)
    if email:
        contacts.extend(query.filter(models.Contact.email == email).all())
    if phone:
        contacts.extend(query.filter(models.Contact.phoneNumber == phone).all())
    return contacts

def create_new_contact(db: Session, email: str = None, phone: str = None):
    new_contact = models.Contact(email=email, phoneNumber=phone, linkPrecedence="primary")
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

def update_contact_as_secondary(db: Session, contact: models.Contact, primary_contact_id: int):
    contact.linkPrecedence = "secondary"
    contact.linkedId = primary_contact_id
    db.commit()
    db.refresh(contact)

def consolidate_contact_data(primary_contact, secondary_contacts):
    emails = [primary_contact.email] + [sc.email for sc in secondary_contacts if sc.email]
    phone_numbers = [primary_contact.phoneNumber] + [sc.phoneNumber for sc in secondary_contacts if sc.phoneNumber]
    secondary_contact_ids = [sc.id for sc in secondary_contacts]

    return {
        "primaryContactId": primary_contact.id,
        "emails": set([email for email in emails if email]),
        "phoneNumbers": set([phone for phone in phone_numbers if phone]),
        "secondaryContactIds": set(secondary_contact_ids)
    }

def get_consolidated_contact(db: Session, email: str, phone: str):
    contacts = find_contact_by_email_or_phone(db, email, phone)

    if contacts:
        primary_contact = min(contacts, key=lambda c: c.createdAt)
        secondary_contacts = [c for c in contacts if c.id != primary_contact.id]

        for contact in secondary_contacts:
            if contact.linkPrecedence != "secondary":
                update_contact_as_secondary(db, contact, primary_contact.id)

        additional_secondary_contacts = db.query(models.Contact).filter(models.Contact.linkedId == primary_contact.id).all()
        secondary_contacts.extend(additional_secondary_contacts)

        return consolidate_contact_data(primary_contact, secondary_contacts)
    
    new_contact = create_new_contact(db, email, phone)
    return {
        "primaryContactId": new_contact.id,
        "emails": [new_contact.email] if new_contact.email else [],
        "phoneNumbers": [new_contact.phoneNumber] if new_contact.phoneNumber else [],
        "secondaryContactIds": []
    }