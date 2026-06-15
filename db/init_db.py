from sqlmodel import SQLModel, Field, create_engine
from typing import Optional

class Course(SQLModel, table=True):
    fetch_date: str = Field(primary_key=True)
    source: str = Field(primary_key=True)
    external_id: str = Field(primary_key=True)
    name: Optional[str] = None
    program_type: Optional[str] = None
    domain: Optional[str] = None
    status: Optional[str] = None
    format: Optional[str] = None
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    payment: Optional[str] = None
    level: Optional[str] = None
    country: Optional[str] = None
    url: Optional[str] = None
    extra: Optional[str] = None  # JSON-рядок


engine = create_engine("sqlite:///downloads/data.db")
SQLModel.metadata.create_all(engine)