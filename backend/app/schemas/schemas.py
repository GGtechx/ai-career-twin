from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date

class HealthCheckResponse(BaseModel):
    status: str
    app_name: str
    database_status: str
    database_type: str
    is_sqlite_fallback: bool
    configured_db_url_masked: str
    tables_registered_count: int
    tables_created_in_db_count: int
    timestamp: datetime

class DatabaseStatus(BaseModel):
    connected: bool
    database_type: str
    total_tables: int
    table_names: List[str]
    details: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "student"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

