import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Supply Chain Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Tracing Middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ── Global Exception Handler ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging
    logger = logging.getLogger("supplyiq")
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "An unexpected error occurred"}},
    )


# ── Health Check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {"status": "healthy", "app": settings.APP_NAME, "version": "1.0.0"}


# ── Routes ─────────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# ── Startup ────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    import logging
    logging.getLogger("supplyiq").info(f"🚀 {settings.APP_NAME} starting up in {settings.APP_ENV} mode")
