import uuid
from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse

def _convert_uuids(obj):
    if isinstance(obj, dict):
        return {k: _convert_uuids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_uuids(v) for v in obj]
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    else:
        return obj

def create_response(
    success: bool,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    error_code: Optional[str] = None,
    status_code: int = 200,
    pagination: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "reqId": str(uuid.uuid4()),
            "meta": { "success": success, "message": message, "error_code": error_code },
            "data": _convert_uuids(data) if data is not None else None,
            "pagination": _convert_uuids(pagination) if pagination is not None else None,
        },
    )