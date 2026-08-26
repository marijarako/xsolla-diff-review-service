"""
Main entry point of the service.

Phase 1: /health and /spec routes (public, no authentication).
Phase 2: authentication middleware protecting all /v1/* routes.
"""
import time
from fastapi import FastAPI
from app.auth import AuthMiddleware

# Service version - we bump this manually on meaningful changes.
# "semver" = Semantic Versioning: MAJOR.MINOR.PATCH
SERVICE_VERSION = "0.1.0"

# Record the moment the service started, so we can compute how long
# it has been running (uptimeSeconds).
START_TIME = time.time()

app = FastAPI(title="AI Diff Review Service", version=SERVICE_VERSION)

app.add_middleware(AuthMiddleware)

@app.get("/health")
def health():
    """
    Public route (no authentication required).
    Returns service status, version, and how long it has been running.
    """
    uptime_seconds = time.time() - START_TIME
    return {
        "status": "ok",
        "version": SERVICE_VERSION,
        "uptimeSeconds": round(uptime_seconds, 2),
    }


@app.get("/spec")
def spec():
    """
    Public route (no authentication required).
    Machine-readable self-declaration: what the service supports and
    its limits. These values MUST match the service's actual behavior
    (this will be checked by automated tests).
    """
    return {
        "specVersion": "1.0",
        "providers": ["mock", "llm"],
        "limits": {
            "maxPayloadBytes": 1048576,     # 1 MiB
            "chunkBytes": 65536,            # 64 KiB
            "maxConcurrentJobs": 4,
            "rateLimitPerMinute": 30,
        },
    }

@app.get("/v1/_authcheck")
def auth_check():
    """
    TEMPORARY route, used only to manually verify the auth middleware
    works before real /v1 routes exist (added in later phases).
    Will be removed once /v1/reviews is implemented.
    """
    return {"authenticated": True}