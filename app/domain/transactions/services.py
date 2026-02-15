from typing import List, Optional
from uuid import UUID

from app.domain.transactions.repositories import TransactionItemData, TransactionRepository
from app.domain.expeditions.repositories import ExpeditionRepository
from app.domain.products.repositories import ProductRepository
from app.domain.carts.repositories import CartRepository
from app.domain.transactions.models import MstTransaction, TrnTransactionStatus, TransactionStatus
from app.domain.transactions.schemas import TransactionCreate, TransactionItem

class TransactionService:
    def __init__(self, transaction_repo: TransactionRepository, expedition_repo: ExpeditionRepository, product_repo: ProductRepository, cart_repo: CartRepository):
        self.transaction_repo = transaction_repo
        self.expedition_repo = expedition_repo
        self.product_repo = product_repo
        self.cart_repo = cart_repo

    async def create_transaction(self, transaction_in: TransactionCreate) -> MstTransaction:
        """Create a transaction using provided items or the user's cart."""
        expedition = await self.expedition_repo.get_expedition_service_by_id(transaction_in.id_expedition_service)
        if not expedition:
            raise ValueError("Expedition service not found")

        used_cart_items = False
        items_payload: List[TransactionItem] = transaction_in.items or []
        if not items_payload:
            carts = await self.cart_repo.get_carts_by_user_id(transaction_in.id_user, limit=1000, offset=0)
            if not carts:
                raise ValueError("No cart items found for the user")
            used_cart_items = True
            items_payload = [
                TransactionItem(
                    id_product=cart.id_product,
                    quantity=cart.quantity,
                    price_at_time=cart.price_at_time,
                )
                for cart in carts
            ]

        transaction_items: List[TransactionItemData] = []
        for item in items_payload:
            if item.quantity <= 0:
                raise ValueError("Quantity must be greater than zero")

            product = await self.product_repo.get_product_by_id(item.id_product)
            if not product:
                raise ValueError(f"Product {item.id_product} not found")

            product_stock = getattr(product, "stock", 0) or 0
            if product_stock < item.quantity:
                raise ValueError(f"Insufficient stock for product {item.id_product}")

            unit_price = item.price_at_time if item.price_at_time is not None else product.price

            transaction_items.append({
                "id_product": item.id_product,
                "quantity": item.quantity,
                "price_at_time": unit_price,
            })

            await self.product_repo.update_product_stock(item.id_product, product_stock - item.quantity)

        new_transaction = await self.transaction_repo.create_transaction(
            id_user=transaction_in.id_user,
            id_expedition_service=transaction_in.id_expedition_service,
            items=transaction_items,
        )

        if used_cart_items:
            await self.cart_repo.empty_cart_by_user_id(transaction_in.id_user)
        return new_transaction

    async def update_transaction_status(self, transaction_id: UUID, status: TransactionStatus) -> Optional[TrnTransactionStatus]:
        return await self.transaction_repo.update_transaction_status(transaction_id, status)

    async def get_transaction_by_id(self, transaction_id: UUID) -> Optional[MstTransaction]:
        return await self.transaction_repo.get_transaction_by_id(transaction_id)

    async def update_expedition_service(self, transaction_id: UUID, expedition_service_id: UUID) -> Optional[MstTransaction]:
        is_pending = await self.transaction_repo.get_transaction_status_by_id(transaction_id)
        if not is_pending or is_pending.status != TransactionStatus.PENDING:
            raise ValueError("Only pending transactions can update expedition service")
        expedition = await self.expedition_repo.get_expedition_service_by_id(expedition_service_id)
        if not expedition:
            raise ValueError("Expedition service not found")
        await self.transaction_repo.update_expedition_service(transaction_id, expedition_service_id)
        return await self.transaction_repo.get_transaction_by_id(transaction_id)

    async def get_all_transactions(
        self,
        *,
        user_id: Optional[UUID] = None,
        status: Optional[TransactionStatus] = None,
        expedition_service: Optional[UUID] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[MstTransaction]:
        return await self.transaction_repo.get_all_transactions(
            user_id=user_id,
            status=status,
            expedition_service=expedition_service,
            limit=limit,
            offset=offset,
        )