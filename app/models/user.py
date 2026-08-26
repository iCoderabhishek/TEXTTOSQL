import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Share the same Base as the rest of the application
from app.models.company import Base

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserSubscription(enum.Enum):
    FREE = "free"
    PLUS = "plus"
    PREMIUM = "premium"

class User(Base):
    __tablename__ = "User"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.GUEST)
    subscription = Column(SQLEnum(UserSubscription), default=UserSubscription.FREE)
    
    company_id = Column(UUID(as_uuid=True), ForeignKey("Company.id"), nullable=False)
    
    ip_address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    phone_number = Column(String, nullable=True)
    oauth_client_id = Column(String, nullable=True)
    oauth_provider = Column(String, nullable=True)  
    
    company = relationship("Company", back_populates="users")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))