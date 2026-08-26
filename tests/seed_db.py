import uuid
import random
from datetime import datetime, timezone

from app.core.db import engine, SessionLocal
from app.models.company import Base, Company, Employee
from app.models.sales import Sales
from app.models.user import User, UserRole, UserSubscription

def seed_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Depup check
    if db.query(Company).first():
        print("Database already seeded. Skipping.")
        db.close()
        return

    print("Seeding Company data...")
    tech_corp = Company(
        company_name="Nexus Data Solutions",
        company_email="admin@nexusdata.io",
        company_city="Seattle",
        company_country="USA",
        company_employees=350
    )
    db.add(tech_corp)
    db.commit()
    db.refresh(tech_corp)

    print("Seeding Employee data...")
    emp1 = Employee(
        first_name="Sarah",
        last_name="Chen",
        email="sarah.chen@nexusdata.io",
        role="Senior Data Engineer",
        compensation=165000,
        company_id=tech_corp.id
    )
    emp2 = Employee(
        first_name="Marcus",
        last_name="Rodriguez",
        email="marcus.r@nexusdata.io",
        role="VP of Sales",
        compensation=210000,
        company_id=tech_corp.id
    )
    db.add_all([emp1, emp2])
    
    print("Seeding Sales data...")
    # 3. Create Sales records
    sale1 = Sales(
        product="Enterprise AI License",
        quantity=2,
        price=50000,
        total_sales=1,
        total_revenue=100000,
        total_profit=80000,
        total_loss=0,
        company_id=tech_corp.id
    )
    sale2 = Sales(
        product="Cloud Storage TB",
        quantity=100,
        price=50,
        total_sales=100,
        total_revenue=5000,
        total_profit=2500,
        total_loss=0,
        company_id=tech_corp.id
    )
    db.add_all([sale1, sale2])
    
    print("Seeding User data...")
    user1 = User(
        username="sarah_c_admin",
        full_name="Sarah Chen",
        email="sarah.chen@nexusdata.io",
        password="pbkdf2_sha256$260000$mock_hash_xyz",
        role=UserRole.ADMIN,
        subscription=UserSubscription.PREMIUM,
        company_id=tech_corp.id
    )
    user2 = User(
        username="marcus_sales",
        full_name="Marcus Rodriguez",
        email="marcus.r@nexusdata.io",
        password="pbkdf2_sha256$260000$mock_hash_abc",
        role=UserRole.USER,
        subscription=UserSubscription.PLUS,
        company_id=tech_corp.id
    )
    db.add_all([user1, user2])
    
    db.commit()
    db.close()
    print("✅ Database successfully seeded!")

if __name__ == "__main__":
    seed_database()
