"""
Authentication middleware.

The contract requires every /v1/* route (any HTTP method, including GET)
to require a valid `Authorization: Bearer <token>` header. /health and
/spec stay public and must NOT go through this check.

Implemented as middleware (instead of a check repeated inside every route
function) so that:
  - every current AND future /v1/* route is protected automatically
  - there is exactly one place in the code deciding "is this request
    authenticated" - easy to test, easy to explain
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import AUTH_TOKEN
from app.errors import error_response


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only routes under /v1/ require authentication.
        if request.url.path.startswith("/v1"):
            header = request.headers.get("authorization")

            if header is None or not header.startswith("Bearer "):
                return error_response(
                    401,
                    "unauthorized",
                    "Missing or malformed Authorization header. "
                    "Expected: Authorization: Bearer <token>",
                )

            token = header.removeprefix("Bearer ").strip()

            if AUTH_TOKEN is None:
                # Misconfiguration on our side (env var not set) - fail
                # closed, never fall back to accepting any request.
                return error_response(
                    401,
                    "unauthorized",
                    "Server auth token is not configured.",
                )

            if token != AUTH_TOKEN:
                return error_response(
                    401,
                    "unauthorized",
                    "Invalid bearer token.",
                )

        # Either this route is public (/health, /spec), or the token
        # was valid - let the request continue to the real route handler.
        response = await call_next(request)
        return response