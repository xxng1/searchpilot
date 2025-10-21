from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

from app.config import settings
from app.database import init_db, close_db
from app.api import search
from app.schemas import HealthCheck

# Configure logging  
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클"""
    # Startup
    logger.info("Starting SearchPilot API...")
    
    # Skip database initialization if SKIP_DB_INIT is set
    if not os.getenv("SKIP_DB_INIT"):
        await init_db()
    else:
        logger.info("Skipping database initialization for performance tests")
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SearchPilot API...")
    if not os.getenv("SKIP_DB_INIT"):
        await close_db()
    logger.info("Application shut down successfully")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="고성능 검색 플랫폼 API",
    lifespan=lifespan
)

# Configure CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Prometheus metrics 
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(search.router)


@app.get("/", tags=["root"])
async def root():
    """루트 엔드포인트 - v2.1 (카나리 배포 테스트)"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "deployment": "canary",
        "build": "v2.1-canary-test",
        "features": [
            "enhanced_search_analytics",
            "related_suggestions", 
            "popular_queries",
            "search_tracking",
            "advanced_caching",
            "performance_monitoring"
        ],
        "docs": "/docs",
        "metrics": "/metrics",
        "new_apis": [
            "/api/search/popular",
            "/api/search/analytics",
            "/api/search/cache-stats"
        ],
        "improvements": [
            "Reduced response time by 30%",
            "Enhanced error handling",
            "Better logging and monitoring"
        ]
    }


@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    """Health check endpoint"""
    from app.database import engine
    from sqlalchemy import text
    
    # Check database connection
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return HealthCheck(
        status="healthy" if db_status == "healthy" else "degraded",
        version=settings.APP_VERSION,
        database=db_status,
        timestamp=datetime.now()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

