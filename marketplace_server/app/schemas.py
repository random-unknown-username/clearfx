from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import datetime

class CreatorResponse(BaseModel):
    handle: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool
    model_config = ConfigDict(from_attributes=True)

class DesignBase(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    license: Optional[str] = None
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    supports_ascii: bool = False
    supports_monochrome: bool = False
    recommended_duration_ms: Optional[int] = None

class DesignResponse(DesignBase):
    slug: str
    current_version: str
    download_count: int
    favorite_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    creator: Optional[CreatorResponse] = None
    model_config = ConfigDict(from_attributes=True)

class DesignListResponse(BaseModel):
    items: List[DesignResponse]
    total: int

class VersionResponse(BaseModel):
    version: str
    changelog: Optional[str] = None
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class ValidationResultResponse(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
