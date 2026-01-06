from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as task_router

from utils.logger import setup_logger
from scheduler.services.db import init_models

# from fastapi import Request
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from scheduler.core.limiter import limiter, rate_limit_handler



logger = setup_logger("Scheduler")

# Initialize FastAPI app
app = FastAPI(title="PyTaskFlow Scheduler")

# Rate limiting setupfrom fastapi import Request

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


# Enable CORS
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    # Basic web config
    ALLOWED_ORIGINS: str = "*"      # keep "*" for local/dev; override in Render
    ALLOW_CREDENTIALS: bool = False

    # Database (common env name)
    DATABASE_URL: Optional[str] = None

    # Worker / coordinator / grpc / heartbeat config
    worker_name: Optional[str] = None
    worker_host: Optional[str] = None
    worker_port: Optional[int] = None
    worker_heartbeat_interval: Optional[int] = None

    coordinator_host: Optional[str] = None
    coordinator_grpc_port: Optional[int] = None
    coordinator_heartbeat_port: Optional[int] = None

    # General scheduler options
    heartbeat_port: Optional[int] = None
    heartbeat_timeout: Optional[int] = None
    check_interval: Optional[int] = None
    task_max_retries: Optional[int] = None
    dispatch_network_retries: Optional[int] = None
    retry_delay: Optional[int] = None
    retry_backoff: Optional[bool] = None

    # Combined config: env_file + ignore unknown env vars
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",   # ignore unknown env vars instead of raising
    )

# instantiate settings
app_settings = AppSettings()

# build origins list from env (support "*" or comma-separated list)
if app_settings.ALLOWED_ORIGINS.strip() == "*" or not app_settings.ALLOWED_ORIGINS:
    origins = ["*"]
else:
    origins = [o.strip() for o in app_settings.ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=app_settings.ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(task_router, prefix="/api", tags=["tasks"])


@app.get("/")
async def root():
    logger.info("Scheduler root endpoint accessed 🚀")
    return {"message": "PyTaskFlow Scheduler running 🚀"}


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Scheduler"}


# Startup event - create DB tables
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database tables 🗄️")
    await init_models()
