"""FastAPI Application Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, simulate, recommend

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Next-Best-Action Customer Intelligence Agent",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Lifespan handlers
@app.on_event("startup")
async def startup_event():
    from app.database import connect_db
    try:
        await connect_db()
        print(f"🚀 {settings.app_name} started on {settings.environment.upper()} mode")
    except Exception as e:
        print(f"⚠️ Could not connect to database: {e}. Running in database-less mode.")


@app.on_event("shutdown")
async def shutdown_event():
    from app.database import disconnect_db
    try:
        await disconnect_db()
    except Exception:
        pass
    print(f"🛑 {settings.app_name} shut down")


# Include routers
app.include_router(health.router)
app.include_router(simulate.router)
app.include_router(recommend.router)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint — verify API is running"""
    return {
        "message": f"{settings.app_name} is running",
        "version": settings.app_version,
        "environment": settings.environment,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
