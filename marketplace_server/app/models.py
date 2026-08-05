import datetime
import enum
from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from .database import Base

class DesignStatus(str, enum.Enum):
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"
    quarantined = "quarantined"

class Creator(Base):
    __tablename__ = "creators"
    id = Column(Integer, primary_key=True, index=True)
    handle = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String)
    email = Column(String, unique=True, index=True)
    bio = Column(Text)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    api_key_hash = Column(String, nullable=False)

    designs = relationship("Design", back_populates="creator")

class Design(Base):
    __tablename__ = "designs"
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    current_version = Column(String, nullable=False)
    license = Column(String)
    tags = Column(JSON)
    min_width = Column(Integer)
    min_height = Column(Integer)
    supports_ascii = Column(Boolean, default=False)
    supports_monochrome = Column(Boolean, default=False)
    recommended_duration_ms = Column(Integer)
    download_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    report_count = Column(Integer, default=0)
    status = Column(String, default=DesignStatus.submitted.value)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    package_hash = Column(String, nullable=False)
    package_size = Column(Integer, nullable=False)

    creator = relationship("Creator", back_populates="designs")
    versions = relationship("DesignVersion", back_populates="design")

class DesignVersion(Base):
    __tablename__ = "design_versions"
    id = Column(Integer, primary_key=True, index=True)
    design_id = Column(Integer, ForeignKey("designs.id"))
    version = Column(String, nullable=False)
    package_hash = Column(String, nullable=False)
    package_size = Column(Integer, nullable=False)
    changelog = Column(Text)
    status = Column(String, default=DesignStatus.submitted.value)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    design = relationship("Design", back_populates="versions")

class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    design_id = Column(Integer, ForeignKey("designs.id"))
    user_ip = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    design_id = Column(Integer, ForeignKey("designs.id"))
    reason = Column(String, nullable=False)
    reporter_ip = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
