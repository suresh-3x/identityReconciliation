import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, services
from .database import engine, Base, get_db

logging.basicConfig(
    level=logging.INFO,  # Set to logging.DEBUG for more detailed logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Ensures logs go to the console
    ]
)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/identify", response_model=schemas.ContactResponse)
def identify_contact(contact: schemas.ContactBase, db: Session = Depends(get_db)):
    if not contact.email and not contact.phoneNumber:
        raise HTTPException(status_code=400, detail="Either email or phone number must be provided")

    response = services.get_consolidated_contact(db, contact.email, contact.phoneNumber)
    return response