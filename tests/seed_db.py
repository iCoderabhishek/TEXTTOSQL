import uuid
import random
from datetime import datetime, timezone

from app.core.db import engine, SessionLocal
from app.models.company import Base, Company, Employee
from app.models.sales import Sales

def seed_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Depup check
    if db.query(Company).first():
        print("Database already seeded. Skipping.")
        db.close()
        return

    print("Seeding Company data...,,,,,,,,,,,,,,,,,,,,,,,,")
    tech_corp = Company(
        company_name="Tech Corp AI",
        company_email="contact@techcorpai.com",
        company_city="San Francisco",
        company_country="USA",
        company_employees=500
    )
    db.add(tech_corp)
    db.commit()
    db.refresh(tech_corp)

    print("Seeding Employee data.........................")
    emp1 = Employee(
        first_name="Alice",
        last_name="Smith",
        email="alice@techcorpai.com",
        role="Data Engineer",
        compensation=120000,
        company_id=tech_corp.id
    )
    emp2 = Employee(
        first_name="Bob",
        last_name="Johnson",
        email="bob@techcorpai.com",
        role="Sales Executive",
        compensation=95000,
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
    
    db.commit()
    db.close()
    print("✅ Database successfully seeded!")

if __name__ == "__main__":
    seed_database()
