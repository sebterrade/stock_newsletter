from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    is_active: bool = Field(default=True)
    
    preferences: List["UserPreference"] = Relationship(back_populates="user")

class Stock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticker: str = Field(index=True, unique=True)
    company_name: Optional[str] = Field(default=None)

class UserPreference(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    ticker: str = Field(foreign_key="stock.ticker")
    
    user: Optional[User] = Relationship(back_populates="preferences")
