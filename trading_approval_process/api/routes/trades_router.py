from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from uuid import UUID
from typing import Annotated
import asyncio

from trading_approval_process.application.services.trade_approval_service import TradeApprovalService
from ...domain.models.trade_details import TradeDetails
from ...domain.models.execution_confirmation import ExecutionConfirmation
from ...core.cancellation_token import CancellationToken
from ..dependencies import get_trade_service

router = APIRouter()

# --- Cancellation token dependency ---
async def get_cancellation_token(request: Request) -> CancellationToken:
    token = CancellationToken()
    async def cancel_on_disconnect():
        await request.is_disconnected()
        token.cancel("Client disconnected")
    asyncio.create_task(cancel_on_disconnect())
    return token

# --- Endpoints ---
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_trade(
    user: Annotated[str, Query(..., description="Requester creating the trade")],
    details: TradeDetails,
    service: TradeApprovalService = Depends(get_trade_service),
    token: CancellationToken = Depends(get_cancellation_token),
):
    try:
        return await service.create(user, details, token)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.post("/{trade_id}/update")
async def update_trade(
    trade_id: UUID,
    user: Annotated[str, Query(..., description="Requester updating the trade")],
    details: TradeDetails,
    service: TradeApprovalService = Depends(get_trade_service),
    token: CancellationToken = Depends(get_cancellation_token),
):
    try:
        return await service.update(user, trade_id, details, token)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.post("/{trade_id}/submit")
async def submit_trade(
    trade_id: UUID,
    user: Annotated[str, Query(..., description="Requester submitting for approval")],
    service: TradeApprovalService = Depends(get_trade_service),
    token: CancellationToken = Depends(get_cancellation_token),
):
    try:
        return await service.submit(user, trade_id, token)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.post("/{trade_id}/approve")
async def approve_trade(
    trade_id: UUID,
    user: Annotated[str, Query(..., description="Approver approving the trade")],
    service: TradeApprovalService = Depends(get_trade_service),
    token: CancellationToken = Depends(get_cancellation_token),
):
    try:
        return await service.approve(user, trade_id, token)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.post("/{trade_id}/cancel")
async def cancel_trade(
    trade_id: UUID,
    user: Annotated[str, Query(..., description="User cancelling the trade")],
    service: TradeApprovalService = Depends(get_trade_service),
    token: CancellationToken = Depends(get_cancellation_token),
):
    try:
        return await service.cancel(user, trade_id, token)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.post("/{trade_id}/send_to_execute")
async def send_to_execute(
    trade_id: UUID,
    user: Annotated[str, Query(..., description="Approver sending to execution venue")],
    service: TradeApprovalService = Depends(get_trade_service),
    token: CancellationToken = Depends(get_cancellation_token),
):
    try:
        return await service.send_to_execute(user, trade_id, token)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.post("/{trade_id}/book")
async def book_trade(
    trade_id: UUID,
    user: Annotated[str, Query(..., description="Requester booking executed trade")],
    confirmation: ExecutionConfirmation,
    service: TradeApprovalService = Depends(get_trade_service),
    token: CancellationToken = Depends(get_cancellation_token),
):
    try:
        return await service.book(user, trade_id, confirmation, token)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("/{trade_id}/history")
async def get_history(
    trade_id: UUID,
    service: TradeApprovalService = Depends(get_trade_service),
    token: CancellationToken = Depends(get_cancellation_token),
):
    try:
        return await service.get_history(trade_id, token)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("/{trade_id}/differences")
async def get_differences(
    trade_id: UUID,
    service: TradeApprovalService = Depends(get_trade_service),
    token: CancellationToken = Depends(get_cancellation_token),
):
    try:
        return await service.get_differences(trade_id, token)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
