from typing import Optional, Sequence, TypedDict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.transactions.models import MstTransaction, TrnTransactionItem, TrnTransactionStatus, TransactionStatus


class TransactionItemData(TypedDict):
    id_product: UUID
    quantity: int
    price_at_time: int

class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_transaction(
        self,
        *,
        id_user: UUID,
        id_expedition_service: UUID,
        items: Sequence[TransactionItemData],
    ) -> MstTransaction:
        total = sum(item["price_at_time"] * item["quantity"] for item in items)

        new_transaction = MstTransaction(
            id_user=id_user,
            total=total,
            id_expedition_service=id_expedition_service,
        )
        self.db.add(new_transaction)
        await self.db.commit()
        await self.db.refresh(new_transaction)

        transaction_items = []
        for item in items:
            transaction_item = TrnTransactionItem(
                id_transaction=new_transaction.id_transaction,
                id_product=item["id_product"],
                quantity=item["quantity"],
                price_at_time=item["price_at_time"],
            )
            transaction_items.append(transaction_item)
        
        transaction_status = TrnTransactionStatus(
            id_transaction=new_transaction.id_transaction,
            status=TransactionStatus.PENDING,
        )
        self.db.add(transaction_status)

        self.db.add_all(transaction_items)
        await self.db.commit()
        for item in transaction_items:
            await self.db.refresh(item)
        await self.db.refresh(transaction_status)
        new_transaction.items = transaction_items  # expose items for response
        new_transaction.status = transaction_status.status  # expose status for response
        return new_transaction
    
    async def update_transaction_status(self, transaction_id: UUID, status: TransactionStatus) -> Optional[TrnTransactionStatus]:
        result = await self.db.execute(select(TrnTransactionStatus).where(TrnTransactionStatus.id_transaction == transaction_id))
        transaction_status = result.scalars().first()
        if not transaction_status:
            return None
        
        transaction_status.status = status
        self.db.add(transaction_status)
        await self.db.commit()
        await self.db.refresh(transaction_status)
        return transaction_status
    
    async def get_transaction_by_id(self, transaction_id: UUID) -> Optional[MstTransaction]:
        result = await self.db.execute(
            select(MstTransaction, TrnTransactionItem, TrnTransactionStatus.status)
            .where(MstTransaction.id_transaction == transaction_id)
            .join(TrnTransactionItem, TrnTransactionItem.id_transaction == MstTransaction.id_transaction)
            .join(TrnTransactionStatus, TrnTransactionStatus.id_transaction == MstTransaction.id_transaction)
        )
        row = result.first()
        if not row:
            return None
        transaction, item, status = row
        transaction.items = [item]  # expose items for response
        transaction.status = status  # expose status for response
        return transaction
    
    async def get_transaction_status_by_id(self, transaction_id: UUID) -> Optional[TrnTransactionStatus]:
        result = await self.db.execute(select(TrnTransactionStatus).where(TrnTransactionStatus.id_transaction == transaction_id))
        return result.scalars().first()
    
    async def update_expedition_service(self, transaction_id: UUID, expedition_service_id: UUID) -> Optional[MstTransaction]:
        result = await self.db.execute(select(MstTransaction).where(MstTransaction.id_transaction == transaction_id))
        transaction = result.scalars().first()
        if not transaction:
            return None
        
        transaction.id_expedition_service = expedition_service_id
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
    
    async def get_all_transactions(
        self,
        user_id: Optional[UUID] = None,
        status: Optional[TransactionStatus] = None,
        expedition_service: Optional[UUID] = None,
        limit: int = 10,
        offset: int = 0,
    ):
        query = (
            select(MstTransaction, TrnTransactionItem, TrnTransactionStatus.status)
            .join(TrnTransactionItem, TrnTransactionItem.id_transaction == MstTransaction.id_transaction)
            .join(TrnTransactionStatus, TrnTransactionStatus.id_transaction == MstTransaction.id_transaction)
            .order_by(MstTransaction.created_at.desc())
        )
        if expedition_service:
            query = query.where(MstTransaction.id_expedition_service == expedition_service)
        if user_id:
            query = query.where(MstTransaction.id_user == user_id)
        if status:
            query = query.where(TrnTransactionStatus.status == status)

        result = await self.db.execute(query.limit(limit).offset(offset))
        transactions_dict = {}
        for transaction, item, status in result.all():
            if transaction.id_transaction not in transactions_dict:
                transaction.items = []  # initialize items list
                transaction.status = status  # expose status for response
                transactions_dict[transaction.id_transaction] = transaction
            transactions_dict[transaction.id_transaction].items.append(item)  # append items to the transaction
        return list(transactions_dict.values())