# app/Services/supabase_auth_service.py

from __future__ import annotations
from uuid import UUID
from typing import Any, Dict, Optional
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.Infrastructure import supabase_auth_client
from app.Repositories.user_role_repository import UserRoleRepository
from app.Schemas.auth_session import (
    LoginInput,
    RegisterInput,
    VerifyMfaInput,
)

class SupabaseAuthService:
    """
    Servizio di alto livello per la gestione dell'autenticazione tramite Supabase.
    Incapsula la logica di business relativa a login, registrazione e MFA.
    """

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db

    async def login(self, payload: LoginInput) -> Dict[str, Any]:
        """
        Esegue il login dell'utente e gestisce l'eventuale richiesta di MFA.
        """
        res = await supabase_auth_client.sign_in(payload.email, payload.password)
        if res.get("error"):
            return res

        access_token = res.get("access_token")
        user_obj = res.get("user") or {}

        # Verifica il livello di Authenticator Assurance Level (AAL)
        aal = None
        try:
            decoded_token = jwt.get_unverified_claims(access_token)
            aal = decoded_token.get("aal")
        except Exception:
            pass

        factors = user_obj.get("factors")

        # Se l'utente ha il MFA abilitato e non è ancora passato al livello aal2
        if aal == "aal1" and factors and len(factors) > 0:
            totp_factor = next((f for f in factors if f.get("factor_type") == "totp" and f.get("status") == "verified"), None)

            if totp_factor and access_token:
                factor_id = totp_factor.get("id")
                chal = await supabase_auth_client.create_mfa_challenge(access_token, factor_id)

                if chal.get("error"):
                    return chal

                challenge_id = chal.get("id")
                if challenge_id:
                    return {
                        "status": "mfa_required",
                        "access_token": access_token,
                        "factor_id": factor_id,
                        "challenge_id": challenge_id,
                    }

        return {
            "status": "success",
            "access_token": access_token,
            "token_type": res.get("token_type"),
            "expires_in": res.get("expires_in"),
            "refresh_token": res.get("refresh_token"),
            "user": user_obj,
        }

    async def verify_mfa(self, payload: VerifyMfaInput) -> Dict[str, Any]:
        """
        Verifica il codice MFA fornito dall'utente.
        """
        return await supabase_auth_client.verify_mfa_challenge(
            payload.access_token, payload.factor_id, payload.challenge_id, payload.code
        )

    async def enroll_totp(self, access_token: str, friendly_name: str) -> Dict[str, Any]:
        """
        Inizia il processo di attivazione del TOTP (MFA).
        """
        user_res = await supabase_auth_client.get_user_from_access_token(access_token)
        if user_res.get("error"):
            return user_res

        if not user_res.get("email_confirmed_at"):
            return {"error": "auth", "message": "Email non confermata", "http_status": 400}

        res = await supabase_auth_client.enroll_totp(access_token, friendly_name=friendly_name)
        if res.get("error"):
            return res

        factor_id = res.get("id")
        totp = res.get("totp") or {}
        chal = await supabase_auth_client.create_mfa_challenge(access_token, factor_id)

        if chal.get("error"):
            return chal

        return {
            "factor_id": factor_id,
            "secret": totp.get("secret"),
            "otpauth_uri": totp.get("uri"),
            "qr_code": totp.get("qr_code"),
            "challenge_id": chal.get("id"),
        }

    async def list_factors(self, access_token: str) -> Dict[str, Any]:
        """
        Elenca i fattori MFA dell'utente.
        """
        return await supabase_auth_client.list_factors(access_token)

    async def delete_factor(self, access_token: str, factor_id: str) -> Dict[str, Any]:
        """
        Elimina un fattore MFA per l'utente.
        """
        return await supabase_auth_client.delete_mfa_factor(access_token, factor_id)

    async def disable_mfa(self, access_token: str, code: str) -> Dict[str, Any]:
        """
        Disabilita il MFA per l'utente corrente previa verifica di un codice OTP.
        """
        user_res = await supabase_auth_client.get_user_from_access_token(access_token)
        if user_res.get("error"):
            return user_res

        factors = user_res.get("factors", [])
        totp_factor = next((f for f in factors if f.get("factor_type") == "totp" and f.get("status") == "verified"), None)
        if not totp_factor:
            return {"error": "auth", "message": "Nessun fattore MFA attivo trovato", "http_status": 404}

        factor_id = totp_factor.get("id")
        challenge_res = await supabase_auth_client.create_mfa_challenge(access_token, factor_id)
        challenge_id = challenge_res.get("id")
        if not challenge_id:
             return {"error": "auth", "message": "Impossibile creare la challenge MFA", "http_status": 500}

        verify_res = await supabase_auth_client.verify_mfa_challenge(access_token, factor_id, challenge_id, code)
        if verify_res.get("error"):
            return verify_res

        aal2_token = verify_res.get("access_token")
        delete_res = await supabase_auth_client.delete_mfa_factor(aal2_token, factor_id)
        if delete_res.get("error"):
            return delete_res

        # Recuperiamo lo stato aggiornato dell'utente dopo la rimozione del fattore
        refreshed_user = await supabase_auth_client.get_user_from_access_token(aal2_token)
        if not refreshed_user.get("error"):
            verify_res["user"] = refreshed_user

        return verify_res

    async def register(self, payload: RegisterInput) -> Dict[str, Any]:
        """
        Registra un nuovo utente e gli assegna il ruolo predefinito.
        """
        user_meta = payload.user_meta or {}
        user_meta['display_name'] = payload.name

        res = await supabase_auth_client.register_user(
            email=payload.email,
            password=payload.password,
            user_meta=user_meta,
            app_meta=payload.app_meta,
            phone=payload.phone,
        )

        if res.get("error"):
            return res

        user = (res.get("user") or {})
        user_id_str = user.get("id")

        if self.db and user_id_str:
            # Assegna il ruolo 'user' predefinito
            user_role_id = UUID("0cc83a82-88f8-4ed9-9c92-ec9e09b266fd")
            repo = UserRoleRepository(self.db)
            try:
                await repo.assign(user_id=UUID(user_id_str), role_id=user_role_id)
            except IntegrityError:
                pass

        return res
