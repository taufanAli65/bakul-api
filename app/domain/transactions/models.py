from datetime import datetime
import uuid
import enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.base_class import Base

class TransactionStatus(str, enum.Enum):
    PAID = "paid"
    PENDING = "pending"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PACKING = "packing"
    COMPLETED = "completed"
    SHIPPED = "shipped"

class MstExpeditionService(Base):
    __tablename__ = "mst_expedition_service"

    id_expedition_service = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)

class MstTransaction(Base):
    __tablename__ = "mst_transactions"

    id_transaction = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    id_user = Column(UUID(as_uuid=True), ForeignKey("mst_users.id_user"))
    id_expedition_service = Column(UUID(as_uuid=True), ForeignKey("mst_expedition_service.id_expedition_service"))
    total = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)

    items = relationship("TrnTransactionItem", back_populates="transaction")
    statuses = relationship("TrnTransactionStatus", back_populates="transaction")

class TrnTransactionItem(Base):
    __tablename__ = "trn_transaction_items"

    id_transaction_item = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    id_transaction = Column(UUID(as_uuid=True), ForeignKey("mst_transactions.id_transaction"))
    id_product = Column(UUID(as_uuid=True), ForeignKey("mst_product.id_product"))
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("MstTransaction", back_populates="items")

class TrnTransactionStatus(Base):
    __tablename__ = "trn_transaction_status"

    id_transaction_status = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    id_transaction = Column(UUID(as_uuid=True), ForeignKey("mst_transactions.id_transaction"))
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transaction = relationship("MstTransaction", back_populates="statuses")
