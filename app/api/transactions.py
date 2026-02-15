from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.core.dependencies import (
	get_current_admin,
	get_current_user,
	get_transaction_service,
)
from app.domain.transactions.helpers import serialize_transaction
from app.domain.transactions.models import TransactionStatus
from app.domain.transactions.schemas import (
	TransactionCreate,
	TransactionCreateRequest,
	TransactionPaymentSimulation,
	TransactionStatusUpdate,
)
from app.domain.transactions.services import TransactionService
from app.domain.users.models import MstUser
from app.utils.response_utils import create_response

router = APIRouter()


@router.post("/", response_model=None)
async def create_transaction(
	payload: TransactionCreateRequest,
	transaction_service: TransactionService = Depends(get_transaction_service),
	current_user: MstUser = Depends(get_current_user),
):
	transaction_in = TransactionCreate(
		id_user=current_user.id_user,
		id_expedition_service=payload.id_expedition_service,
		items=payload.items,
	)
	try:
		transaction = await transaction_service.create_transaction(transaction_in)
	except ValueError as exc:
		return create_response(
			success=False,
			message=str(exc),
			error_code="TRANSACTION_CREATE_FAILED",
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	return create_response(
		success=True,
		message="Transaction created successfully",
		data=serialize_transaction(transaction),
		status_code=status.HTTP_201_CREATED,
	)


@router.get("/", response_model=None)
async def list_transactions(
	transaction_service: TransactionService = Depends(get_transaction_service),
	current_user: MstUser = Depends(get_current_user),
	user_id: Optional[UUID] = None,
	status_filter: Optional[TransactionStatus] = None,
	expedition_service: Optional[UUID] = None,
	limit: int = 10,
	offset: int = 0,
):
	effective_user_id = user_id if current_user.role == "admin" else current_user.id_user

	transactions = await transaction_service.get_all_transactions(
		user_id=effective_user_id,
		status=status_filter,
		expedition_service=expedition_service,
		limit=limit,
		offset=offset,
	)

	return create_response(
		success=True,
		message="Transactions retrieved successfully",
		data=[serialize_transaction(tx) for tx in transactions],
		status_code=status.HTTP_200_OK,
		pagination={
			"limit": limit,
			"offset": offset,
			"total": len(transactions),
		},
	)


@router.get("/{transaction_id}", response_model=None)
async def get_transaction(
	transaction_id: UUID,
	transaction_service: TransactionService = Depends(get_transaction_service),
	current_user: MstUser = Depends(get_current_user),
):
	transaction = await transaction_service.get_transaction_by_id(transaction_id)
	if not transaction:
		return create_response(
			success=False,
			message="Transaction not found",
			error_code="TRANSACTION_NOT_FOUND",
			status_code=status.HTTP_404_NOT_FOUND,
		)

	if current_user.role != "admin" and transaction.id_user != current_user.id_user:
		return create_response(
			success=False,
			message="Not authorized to view this transaction",
			error_code="FORBIDDEN",
			status_code=status.HTTP_403_FORBIDDEN,
		)

	return create_response(
		success=True,
		message="Transaction retrieved successfully",
		data=serialize_transaction(transaction),
		status_code=status.HTTP_200_OK,
	)


@router.put("/{transaction_id}/status", response_model=None)
async def update_transaction_status(
	transaction_id: UUID,
	payload: TransactionStatusUpdate,
	transaction_service: TransactionService = Depends(get_transaction_service),
	current_user: MstUser = Depends(get_current_admin),
):
	updated_status = await transaction_service.update_transaction_status(transaction_id, payload.status)
	if not updated_status:
		return create_response(
			success=False,
			message="Transaction not found",
			error_code="TRANSACTION_NOT_FOUND",
			status_code=status.HTTP_404_NOT_FOUND,
		)

	return create_response(
		success=True,
		message="Transaction status updated successfully",
		data={
			"transaction_id": transaction_id,
			"status": updated_status.status,
		},
		status_code=status.HTTP_200_OK,
	)


@router.put("/{transaction_id}/expedition", response_model=None)
async def update_transaction_expedition(
	transaction_id: UUID,
	expedition_service_id: UUID,
	transaction_service: TransactionService = Depends(get_transaction_service),
	current_user: MstUser = Depends(get_current_user),
):
	transaction = await transaction_service.get_transaction_by_id(transaction_id)
	if not transaction:
		return create_response(
			success=False,
			message="Transaction not found",
			error_code="TRANSACTION_NOT_FOUND",
			status_code=status.HTTP_404_NOT_FOUND,
		)

	if current_user.role != "admin" and transaction.id_user != current_user.id_user:
		return create_response(
			success=False,
			message="Not authorized to update this transaction",
			error_code="FORBIDDEN",
			status_code=status.HTTP_403_FORBIDDEN,
		)

	try:
		updated = await transaction_service.update_expedition_service(transaction_id, expedition_service_id)
	except ValueError as exc:
		return create_response(
			success=False,
			message=str(exc),
			error_code="TRANSACTION_UPDATE_FAILED",
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	return create_response(
		success=True,
		message="Expedition service updated successfully",
		data=serialize_transaction(updated),
		status_code=status.HTTP_200_OK,
	)


@router.post("/simulation/payment", response_model=None)
async def simulate_payment(
	payload: TransactionPaymentSimulation,
	transaction_service: TransactionService = Depends(get_transaction_service),
	current_user: MstUser = Depends(get_current_user),
):
	transaction = await transaction_service.get_transaction_by_id(payload.transaction_id)
	if not transaction:
		return create_response(
			success=False,
			message="Transaction not found",
			error_code="TRANSACTION_NOT_FOUND",
			status_code=status.HTTP_404_NOT_FOUND,
		)

	if current_user.role != "admin" and transaction.id_user != current_user.id_user:
		return create_response(
			success=False,
			message="Not authorized to update this transaction",
			error_code="FORBIDDEN",
			status_code=status.HTTP_403_FORBIDDEN,
		)

	current_status = getattr(transaction, "status", None)
	if current_status not in (None, TransactionStatus.PENDING):
		return create_response(
			success=False,
			message="Only pending transactions can be paid",
			error_code="INVALID_STATUS",
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	updated_status = await transaction_service.update_transaction_status(payload.transaction_id, TransactionStatus.PAID)
	if not updated_status:
		return create_response(
			success=False,
			message="Transaction not found",
			error_code="TRANSACTION_NOT_FOUND",
			status_code=status.HTTP_404_NOT_FOUND,
		)

	updated_transaction = await transaction_service.get_transaction_by_id(payload.transaction_id)
	return create_response(
		success=True,
		message="Payment simulated successfully",
		data=serialize_transaction(updated_transaction),
		status_code=status.HTTP_200_OK,
	)
