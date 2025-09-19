from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Any, Optional

def format_response(
    data: Any = None,
    message: Optional[str] = None,
    success: bool = True,
    metadata: Any = None,
    http_code: int = 200
) -> JSONResponse:
    content = {
        "http_code": http_code,
        "success": success,
        "message": message if message else "",
        "metadata": metadata if metadata else {},
        "data": data
    }
    encoded_content = jsonable_encoder(content)
    return JSONResponse(status_code=http_code, content=encoded_content)
