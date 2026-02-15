from app.domain.transactions.models import MstTransaction


def serialize_transaction(transaction: MstTransaction) -> dict:
    items = []
    for item in getattr(transaction, "items", []) or []:
        items.append(
            {
                "id": getattr(item, "id_transaction_item", None),
                "product_id": getattr(item, "id_product", None),
                "quantity": getattr(item, "quantity", None),
                "price_at_time": getattr(item, "price_at_time", None),
            }
        )
    return {
        "id": getattr(transaction, "id_transaction", None),
        "user_id": getattr(transaction, "id_user", None),
        "expedition_service_id": getattr(transaction, "id_expedition_service", None),
        "total": getattr(transaction, "total", None),
        "status": getattr(transaction, "status", None),
        "items": items,
    }
