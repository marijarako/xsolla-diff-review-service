"""
Shared error envelope helper.

Every non-2xx response in this service must use the same JSON shape:

    { "error": { "code": "<machine_code>", "message": "<human text>" } }

Centralizing this in one function guarantees every error response -
across every route we add in later phases - has the same shape, instead
of us retyping this dict (and risking typos) in ten different places.
"""

from fastapi.responses import JSONResponse


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """
    Build a JSONResponse using the error envelope required by the contract.

    status_code: the HTTP status code to return (401, 413, 422, ...)
    code: machine-readable error code - must be one of the codes listed
          in the contract (e.g. "unauthorized", "invalid_diff", ...)
    message: human-readable explanation
    """
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )