import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship
class Base(DeclarativeBase):
    pass

class Company(Base):
    __tablename__ = "Company"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    company_name = Column(String)
    company_email = Column(String)
    company_phone = Column(String)
    company_address = Column(String)
    company_city = Column(String)
    company_state = Column(String)
    company_zip = Column(String)
    company_country = Column(String)
    company_logo = Column(String)
    company_website = Column(String)
    company_employees = Column(Integer)
    

    employees = relationship("Employee", back_populates="company")
    sales = relationship("Sales", back_populates="company")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    

class Employee(Base):
    __tablename__ = "Employee"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    zip = Column(String)
    country = Column(String)
    role = Column(String)
    compensation = Column(Integer)
    
    company_id = Column(UUID(as_uuid=True), ForeignKey("Company.id"))    
    
    company = relationship("Company", back_populates="employees")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))