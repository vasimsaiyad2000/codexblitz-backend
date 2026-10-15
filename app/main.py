
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes.analyze import router as analyze_router
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.session import Base, engine
from app.models.project import Project  # Register ORM model


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Local development bootstrap only.
    # Use Alembic migrations for production.
    if settings.app_env == "development":
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    max_age=600,
)

app.include_router(analyze_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
