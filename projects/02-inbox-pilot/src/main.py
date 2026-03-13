"""Inbox Pilot - AI-powered email classification and auto-response service."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import stats, webhook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler for startup and shutdown events."""
    logger.info("Inbox Pilot starting up...")
    yield
    logger.info("Inbox Pilot shutting down...")


app = FastAPI(
    title="Inbox Pilot",
    description=(
        "AI-powered email classification and auto-response service. "
        "Receives Gmail push notifications, classifies emails by category "
        "and sentiment, and generates intelligent auto-responses."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)
app.include_router(stats.router)


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "inbox-pilot"}


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "inbox-pilot",
        "version": "1.0.0",
    }
