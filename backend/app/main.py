"""
AgentReady Lab — FastAPI Application Entry Point.
Adversarial crash-testing and dual-ledger reconciliation platform for AI agent commerce.
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1_router import router as v1_router
from app.api.webhooks import router as webhooks_router
from app.core.config import get_settings, setup_sensitive_log_redaction
from app.schemas.problem_details import (
    ProblemDetails,
    ProblemErrorCode,
    ProblemException,
)

# Apply sensitive log filter (redacts 16-digit PAN, Bearer tokens, API keys)
setup_sensitive_log_redaction()

settings = get_settings()

app = FastAPI(
    title="AgentReady Lab API",
    description="Adversarial crash-testing, dual-ledger reconciliation, and self-healing for agentic commerce stores.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable CORS for Next.js frontend and external developer tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# RFC 9457 Problem Details Exception Handlers
# -----------------------------------------------------------------------------

@app.exception_handler(ProblemException)
async def problem_exception_handler(request: Request, exc: ProblemException) -> JSONResponse:
    """Handles RFC 9457 Problem Details domain exceptions."""
    return JSONResponse(
        status_code=exc.status,
        content=exc.problem.model_dump(exclude_none=True),
        media_type="application/problem+json",
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Formats Pydantic validation errors as RFC 9457 Problem Details."""
    problem = ProblemDetails(
        type="https://lab.example/errors/validation-error",
        title="Invalid Request Payload",
        status=422,
        code=ProblemErrorCode.INVALID_PAYLOAD,
        detail="The request body or parameters failed schema validation.",
        details={"errors": exc.errors()},
    )
    return JSONResponse(
        status_code=422,
        content=problem.model_dump(exclude_none=True),
        media_type="application/problem+json",
    )


# -----------------------------------------------------------------------------
# Core Health & Router Mounts
# -----------------------------------------------------------------------------

@app.get(
    "/healthz",
    tags=["Health"],
    operation_id="healthCheck",
    summary="Health check and warm-up",
    description="Returns service vitality and configuration status. Prevents cold starts on Render.",
)
def health_check() -> dict:
    return {
        "status": "ok",
        "version": "1.0.0",
        "mock_blueprint": settings.use_mock_blueprint,
        "paypal_base_url": settings.PAYPAL_BASE_URL,
    }


# Mount all /v1/* endpoints and live PayPal webhook listener
app.include_router(v1_router)
app.include_router(webhooks_router)

