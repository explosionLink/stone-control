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
# Se necessario, decommentare e configurare qui o in un modulo Core/static.py
# from fastapi.staticfiles import StaticFiles
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclusione dei router
app.include_router(health_router, prefix="/api/v1")
app.include_router(main_router)
