from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.routers import stocks, forex, indices, news, screener, macro, economic_calendar
from app.services.cache_service import cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: inisialisasi cache
    await cache.initialize()
    yield
    # Shutdown: cleanup
    await cache.close()


app = FastAPI(
    title="Financial Dashboard API",
    description="API untuk data saham Indonesia (IDX) dan Forex",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - izinkan frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Daftarkan routers
app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks IDX"])
app.include_router(forex.router, prefix="/api/forex", tags=["Forex"])
app.include_router(indices.router, prefix="/api/indices", tags=["Indices"])
app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(screener.router, prefix="/api/screener", tags=["Screener"])
app.include_router(macro.router, prefix="/api/macro", tags=["Macro"])
app.include_router(economic_calendar.router, prefix="/api/economic-calendar", tags=["Economic Calendar"])


@app.get("/")
async def root():
    return {"status": "ok", "message": "Financial Dashboard API Running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
