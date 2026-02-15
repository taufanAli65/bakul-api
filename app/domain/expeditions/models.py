from datetime import datetime
import uuid
import enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base_class import Base

class MstExpeditionService(Base):
    __tablename__ = "mst_expedition_service"

    id_expedition_service = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)