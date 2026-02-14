from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base_class import Base

class MstCart(Base):
    __tablename__ = "mst_carts"

    id_cart = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    id_product = Column(UUID(as_uuid=True), ForeignKey("mst_product.id_product"))
    id_user = Column(UUID(as_uuid=True), ForeignKey("mst_users.id_user"))
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)

    product = relationship("MstProduct")
    user = relationship("MstUser")
