from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import analytics, health, pollution, weather
from etl.config import get_settings

settings = get_settings()

app = FastAPI(
    title="API Calidad del Aire - Santiago",
    description="API REST para monitoreo y analisis de calidad del aire en Santiago",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(pollution.router)
app.include_router(weather.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {
        "message": "API Calidad del Aire - Santiago",
        "docs": "/docs",
        "health": "/health",
    }
