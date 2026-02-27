# app/Core/rate_limiter.py

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

def key_func_excluding_options(request: Request) -> str:
    """
    Funzione chiave personalizzata per escludere le richieste OPTIONS dal rate limiting.
    """
    if request.method == "OPTIONS":
        return None
    return get_remote_address(request)

# Istanza globale del Limiter
limiter = Limiter(key_func=key_func_excluding_options)
