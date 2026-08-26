from pydantic import BaseModel

class User(BaseModel):

    username: str 
    full_name: str | None = None
    email: str
    password: str | None = None
    role: str | None = None
    subscription: str | None = None
    company_id: str | None = None
    ip_address: str | None = None
    is_active: bool | None = None
    phone_number: str | None = None
    oauth_client_id: str | None = None
    oauth_provider: str | None = None  
    created_at: str | None = None
    updated_at: str | None = None
    
