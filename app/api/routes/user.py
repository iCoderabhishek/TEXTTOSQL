from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.core.db import get_db
from app.models.user import User, UserRole
from app.models.company import Company

router = APIRouter(prefix="/users", tags=["Users"])

class GuestUserCreate(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    
@router.post("/guest", status_code=status.HTTP_201_CREATED)
def create_guest_user(user_in: GuestUserCreate, db: Session = Depends(get_db)):
    """
    Create a new guest user. A default company is created for the user.
    """
    # Check if user exists
    query = db.query(User).filter(User.username == user_in.username)
    if user_in.email:
        query = db.query(User).filter(
            (User.username == user_in.username) | (User.email == user_in.email)
        )
        
    existing_user = query.first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
        
    # Auto-generate email for guest if not provided
    final_email = user_in.email or f"{user_in.username}_{uuid.uuid4().hex[:6]}@guest.local"
        
    # Create a default company for the guest
    company = Company(
        company_name=f"{user_in.username}'s Guest Company"
    )
    db.add(company)
    db.flush() # flush to get company.id
    
    # Create the user
    new_user = User(
        username=user_in.username,
        email=final_email,
        full_name=user_in.full_name,
        role=UserRole.GUEST,
        company_id=company.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "Guest user created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role.value,
            "company_id": new_user.company_id
        }
    }

@router.get("/guest", status_code=status.HTTP_200_OK)
def get_all_guest_users(db: Session = Depends(get_db)):
    """
    Get all guest users.
    """
    users = db.query(User).filter(User.role == UserRole.GUEST).all()
    
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "company_id": user.company_id
        }
        for user in users
    ]
