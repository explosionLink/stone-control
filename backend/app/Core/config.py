# app/config.py
import os
from dotenv import load_dotenv, find_dotenv

# Caricamento esplicito del file .env per garantire che le variabili siano disponibili
# indipendentemente da come viene avviato il processo (es. Alembic)
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

from typing import Optional, List
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Cerca il file .env sia nella cartella corrente che in quella superiore (root del progetto)
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "My FastAPI App"
    ENV: str = "dev"
    SERVER_HOST: str = "http://localhost:8000"

    # Trattiamo CORS_ORIGINS come stringa "semplice" per evitare json.loads automatico di Pydantic
    # Esempi validi in .env:
    #   CORS_ORIGINS=http://localhost:5173
    #   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
    CORS_ORIGINS: Optional[str] = Field(default="http://localhost:5173")

    DB_SSL_VERIFY: bool = True

    DATABASE_URL: Optional[str] = Field(default=None)
    DATABASE_ALEMBIC_URL: Optional[str] = Field(default=None)
    DB_HOST: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_PORT: Optional[int] = 5432
    DB_CHARSET: Optional[str] = "utf8"

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str  # Public key for frontend/client-side
    SUPABASE_SERVICE_KEY: str # Secret key for backend/admin operations
    AUTH_AUTO_CONFIRM_DEV: bool = True

    def assemble_db_url(self, url: Optional[str] = None) -> str:
        if url is None:
            url = self.DATABASE_URL

        if url:
            url = url.strip()
            # Forza l'uso del driver asyncpg
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)

        if not url:
            if not (self.DB_HOST and self.DB_NAME and self.DB_USER and self.DB_PASS):
                raise ValueError("Devi impostare DATABASE_URL oppure tutte le variabili DB_*")
            from urllib.parse import quote_plus
            user = self.DB_USER
            pwd = quote_plus(self.DB_PASS)
            url = f"postgresql+asyncpg://{user}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        # Pulizia URL per asyncpg (non supporta sslmode nella query string)
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        u = urlparse(url)
        if u.query:
            qs = parse_qs(u.query)
            qs.pop('sslmode', None)
            qs.pop('ssl', None)
            new_query = urlencode(qs, doseq=True)
            url = urlunparse(u._replace(query=new_query))

        return url

    def get_old_assemble_logic(self) -> str:
        # Keep this for compatibility if needed elsewhere
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if not (self.DB_HOST and self.DB_NAME and self.DB_USER and self.DB_PASS):
            raise ValueError("Devi impostare DATABASE_URL oppure tutte le variabili DB_*")
        user = self.DB_USER
        from urllib.parse import quote_plus
        pwd = quote_plus(self.DB_PASS)
        return f"postgresql+asyncpg://{user}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def debug_print_config(self):
        """Stampa informazioni diagnostiche sulla configurazione (oscurando i segreti)."""
        import socket
        from urllib.parse import urlparse

        def get_sanitized(url):
            if not url: return "N/A"
            u = urlparse(self.assemble_db_url(url))
            return f"{u.scheme}://{u.username}:****@{u.hostname}:{u.port}{u.path}"

        print(f"--- Configuration Debug ---")
        print(f"APP_NAME: {self.APP_NAME}")
        print(f"ENV: {self.ENV}")
        print(f"DATABASE_URL: {get_sanitized(self.DATABASE_URL)}")
        print(f"DATABASE_ALEMBIC_URL: {get_sanitized(self.DATABASE_ALEMBIC_URL)}")
        print(f"SUPABASE_URL: {self.SUPABASE_URL}")

        for name, url_val in [("App DB", self.DATABASE_URL), ("Alembic DB", self.DATABASE_ALEMBIC_URL)]:
            if url_val:
                u = urlparse(self.assemble_db_url(url_val))
                if u.hostname:
                    try:
                        socket.getaddrinfo(u.hostname, u.port or 5432)
                        print(f"DNS Check ({name}): Host '{u.hostname}' risolvibile.")
                    except socket.gaierror:
                        print(f"DNS Check ({name}): !!! ERRORE !!! L'host '{u.hostname}' non è risolvibile.")

        print(f"---------------------------")

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Converte la stringa CORS_ORIGINS in una lista e aggiunge origini di sviluppo comuni.
        """
        # Set di base per lo sviluppo, per garantire che funzioni localmente
        # a prescindere dal file .env
        # Set di base per lo sviluppo, per garantire che funzioni localmente
        # a prescindere dal file .env. Aggiungiamo più porte comuni per Vite.
        origins = {
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:8000", # Allow backend's own origin
        }

        # For development, allowing wildcard is often useful but can be insecure.
        # The explicit list above is safer. We will keep the wildcard for 'dev' env
        # as a fallback.
        if self.ENV == "dev":
            origins.add("*")

        if self.CORS_ORIGINS:
            # Aggiunge le origini definite nell'ambiente
            custom_origins = {x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()}
            origins.update(custom_origins)

        return list(origins)

settings = Settings()
settings.DATABASE_URL = settings.assemble_db_url()
