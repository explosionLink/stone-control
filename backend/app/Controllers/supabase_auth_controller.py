# app/Controllers/supabase_auth_controller.py

from __future__ import annotations
from uuid import UUID
from fastapi import Depends, HTTPException, status, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db_supabase import get_db
from app.Router.supabase_auth import get_current_claims
from app.Services.supabase_auth_service import SupabaseAuthService
from app.Schemas.auth_session import (
    LoginInput,
    LoginResponse,
    RegisterInput,
    RegisterResponse,
    LogoutResponse,
    LoginMfaChallenge,
    VerifyMfaInput,
    VerifyMfaResponse,
    TotpEnrollInput,
    TotpEnrollResponse,
    ListFactorsResponse,
    MfaDisableInput,
)
from app.Infrastructure import supabase_auth_client

bearer = HTTPBearer(auto_error=True)

class SupabaseAuthController:
    """
    Controller per la gestione dell'autenticazione tramite Supabase.
    Gestisce le richieste HTTP e delega la logica di business al SupabaseAuthService.
    """

    def __init__(self) -> None:
        pass

    async def login(self, payload: LoginInput) -> LoginResponse | LoginMfaChallenge:
        """
        Endpoint per il login dell'utente.
        Supporta il flusso standard e quello con MFA.
        """
        svc = SupabaseAuthService()
        res = await svc.login(payload)

        if res.get("error"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=res.get("message") or "Credenziali non valide"
            )

        if res.get("status") == "mfa_required":
            return LoginMfaChallenge(
                status="mfa_required",
                access_token=res.get("access_token"),
                factor_id=res.get("factor_id"),
                challenge_id=res.get("challenge_id"),
            )

        return LoginResponse(
            access_token=res.get("access_token"),
            token_type=res.get("token_type"),
            expires_in=res.get("expires_in"),
            refresh_token=res.get("refresh_token"),
            user=res.get("user"),
        )

    async def verify_mfa(self, payload: VerifyMfaInput) -> VerifyMfaResponse:
        """
        Endpoint per la verifica del codice MFA.
        """
        svc = SupabaseAuthService()
        res = await svc.verify_mfa(payload)

        if res.get("error"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=res.get("message") or "Codice OTP non valido"
            )

        return VerifyMfaResponse(
            access_token=res.get("access_token") or payload.access_token,
            token_type=res.get("token_type") or "bearer",
            expires_in=res.get("expires_in"),
            refresh_token=res.get("refresh_token"),
            user=res.get("user") or {"mfa_status": "verified"},
        )

    async def enroll_totp(
        self,
        payload: TotpEnrollInput | None = None,
        creds: HTTPAuthorizationCredentials = Depends(bearer),
    ) -> TotpEnrollResponse:
        """
        Endpoint per l'attivazione del MFA (TOTP).
        """
        access_token = creds.credentials
        friendly = payload.friendly_name if payload else "Authenticator"

        svc = SupabaseAuthService()
        res = await svc.enroll_totp(access_token, friendly)

        if res.get("error"):
            status_code = res.get("http_status") or status.HTTP_400_BAD_REQUEST
            raise HTTPException(status_code=status_code, detail=res.get("message"))

        return TotpEnrollResponse(**res)

    async def list_factors(
        self, creds: HTTPAuthorizationCredentials = Depends(bearer)
    ) -> ListFactorsResponse:
        """
        Endpoint per elencare i fattori MFA dell'utente.
        """
        svc = SupabaseAuthService()
        res = await svc.list_factors(creds.credentials)
        if res.get("error"):
            raise HTTPException(status_code=400, detail=res.get("message") or "Errore recupero fattori")
        return ListFactorsResponse(factors=res.get("factors", []))

    async def delete_factor(
        self,
        factor_id: str = Path(..., description="ID del fattore TOTP da eliminare"),
        creds: HTTPAuthorizationCredentials = Depends(bearer),
    ) -> LogoutResponse:
        """
        Endpoint per eliminare un fattore MFA.
        """
        svc = SupabaseAuthService()
        res = await svc.delete_factor(creds.credentials, factor_id)
        if isinstance(res, dict) and res.get("error"):
            status_code = int(res.get("http_status") or 400)
            raise HTTPException(status_code=status_code, detail=res.get("message"))
        return LogoutResponse(ok=True)

    async def disable_mfa(
        self,
        payload: MfaDisableInput,
        creds: HTTPAuthorizationCredentials = Depends(bearer),
    ) -> VerifyMfaResponse:
        """
        Endpoint per disabilitare il MFA.
        """
        svc = SupabaseAuthService()
        res = await svc.disable_mfa(creds.credentials, payload.code)

        if res.get("error"):
            status_code = res.get("http_status") or 500
            raise HTTPException(status_code=status_code, detail=res.get("message"))

        return VerifyMfaResponse(
            access_token=res.get("access_token"),
            token_type=res.get("token_type", "bearer"),
            expires_in=res.get("expires_in"),
            refresh_token=res.get("refresh_token"),
            user=res.get("user") or res,
        )

    async def register(
        self,
        payload: RegisterInput,
        db: AsyncSession = Depends(get_db),
    ) -> RegisterResponse:
        """
        Endpoint per la registrazione di un nuovo utente.
        """
        svc = SupabaseAuthService(db)
        res = await svc.register(payload)

        if res.get("error"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res.get("message"))

        user = res.get("user") or {}
        user_id_str = user.get("id")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="ID utente mancante nella risposta")

        return RegisterResponse(user_id=user_id_str, email=user.get("email"), user=user)

    async def logout(
        self,
        claims=Depends(get_current_claims),
    ) -> LogoutResponse:
        """
        Endpoint per il logout dell'utente.
        """
        user_id = claims.get("sub")
        if user_id:
            res = await supabase_auth_client.admin_logout_user(user_id)
            if res.get("error"):
                status_code = int(res.get("http_status") or 502)
                raise HTTPException(status_code=status_code, detail=res.get("message"))
        return LogoutResponse(ok=True)
