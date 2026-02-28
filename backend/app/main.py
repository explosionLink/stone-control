# app/main.py

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.Router.routes import router as main_router
from app.Router.health import router as health_router
from app.Core.config import settings
from app.Core.rate_limiter import limiter
from app.Core.middleware_config import setup_middlewares

# Inizializzazione dell'app FastAPI
app = FastAPI(title=settings.APP_NAME)

# Configurazione del Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurazione dei Middleware (CORS, Security Headers, ecc.)
setup_middlewares(app)

# --- Mount Static Files (opzionale) ---
import os
from fastapi.staticfiles import StaticFiles

# Assicuriamoci che la cartella outputs esista
outputs_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
if not os.path.exists(outputs_dir):
    os.makedirs(outputs_dir, exist_ok=True)

app.mount("/api/v1/outputs", StaticFiles(directory=outputs_dir), name="outputs")

# Inclusione dei router
app.include_router(health_router, prefix="/api/v1")
app.include_router(main_router)
