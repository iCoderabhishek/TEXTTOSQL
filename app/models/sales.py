import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.company import Base

class Sales(Base):
    __tablename__ = "Sales"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    product = Column(String)
    quantity = Column(Integer)
    price = Column(Integer)
    import_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_sales = Column(Integer)
    total_revenue = Column(Integer)
    total_profit = Column(Integer)
    
    total_loss = Column(Integer)
    
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    company_id = Column(UUID(as_uuid=True), ForeignKey("Company.id"))

    company = relationship("Company", back_populates="sales")