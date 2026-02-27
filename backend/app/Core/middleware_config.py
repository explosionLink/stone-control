# app/Core/middleware_config.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.Core.config import settings
from app.Middleware.security_headers import SecurityHeadersMiddleware

def setup_middlewares(app: FastAPI) -> None:
    """
    Configura i middleware per l'applicazione FastAPI.
    """
    # Middleware per gli header di sicurezza personalizzati
    app.add_middleware(SecurityHeadersMiddleware)

    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
