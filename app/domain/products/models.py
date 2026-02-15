from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base_class import Base

class MstProduct(Base):
    __tablename__ = "mst_product"

    id_product = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    product_image_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)

    stocks = relationship("TrnProductStock", cascade="all, delete-orphan", back_populates="product")

class TrnProductStock(Base):
    __tablename__ = "trn_product_stock"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    id_product = Column(UUID(as_uuid=True), ForeignKey("mst_product.id_product", ondelete="CASCADE"))
    stock = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("MstProduct", back_populates="stocks")
