from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os
from contextlib import asynccontextmanager

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.config import settings
from core.database import engine, Base
from core.module_registry import ModuleRegistry
from core.exceptions import setup_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting BEC CRM API")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize module registry
    module_registry = ModuleRegistry()
    await module_registry.initialize()

    # Register module routers
    module_registry.register_routers(app)

    app.state.module_registry = module_registry

    logger.info("API startup complete")

    yield

    # Shutdown
    logger.info("Shutting down BEC CRM API")
    await module_registry.cleanup()


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Health check endpoint
@app.get("/api/v1/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "bec-crm-api"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/api/v1/healthz"
    }

# Module routes will be registered by the ModuleRegistry during startup

# TEMPORARY: Keep auth workaround active for login (module auth has ORM relationship issues)
try:
    from auth_workaround import router as auth_workaround_router
    # Register at a different path to avoid conflicts
    app.include_router(auth_workaround_router, prefix="/api/v1", tags=["Auth-Workaround"])
    logger.info("✅ Registered auth workaround for login")
except Exception as e:
    logger.error(f"❌ Failed to register auth workaround: {e}")

# Clients API using central models
try:
    from clients_api import router as clients_router
    app.include_router(clients_router, prefix="/api/v1")
    logger.info("✅ Registered clients API")
except Exception as e:
    logger.error(f"❌ Failed to register clients API: {e}")
    import traceback
    logger.error(traceback.format_exc())

# Memberships API
try:
    from memberships_api import router as memberships_router
    app.include_router(memberships_router, prefix="/api/v1")
    logger.info("✅ Registered memberships API")
except Exception as e:
    logger.error(f"❌ Failed to register memberships API: {e}")
    import traceback
    logger.error(traceback.format_exc())

# Check-ins stats API
try:
    from checkins_api import router as checkins_router
    app.include_router(checkins_router, prefix="/api/v1")
    logger.info("✅ Registered check-ins API")
except Exception as e:
    logger.error(f"❌ Failed to register check-ins API: {e}")
    import traceback
    logger.error(traceback.format_exc())

# Users/Staff management API (admin only)
try:
    from users_api import router as users_router
    app.include_router(users_router, prefix="/api/v1")
    logger.info("✅ Registered users management API")
except Exception as e:
    logger.error(f"❌ Failed to register users API: {e}")
    import traceback
    logger.error(traceback.format_exc())