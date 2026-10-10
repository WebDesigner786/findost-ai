"""CORS Middleware Configuration"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


def setup_cors(app: FastAPI) -> None:
    """Configures CORS headers to allow requests from authorized frontend origins."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            settings.DEMO_USER_HEADER,
            "Accept",
            "Origin",
            "X-Requested-With",
        ],
        expose_headers=["X-Process-Time"],
    )
