# app/Schemas/supabase_session.py

from __future__ import annotations
from typing import Any, Dict, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

# ───────────── Ingressi ─────────────

class SupabaseLoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class SupabaseRegisterInput(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)
    user_meta: Optional[Dict[str, Any]] = None
    app_meta: Optional[Dict[str, Any]] = None
    phone: Optional[str] = None

    @field_validator('confirm_password')
    def passwords_match(cls, v: str, values: Dict[str, Any]) -> str:
        if 'password' in values.data and v != values.data['password']:
            raise ValueError('Le password non corrispondono')
        return v

# ───────────── Uscite ─────────────

class SupabaseLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    user: Dict[str, Any]

class SupabaseRegisterResponse(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    user: Dict[str, Any]
    status: str = "registered"

class SupabaseLogoutResponse(BaseModel):
    ok: bool = True

# ───────────── MFA ─────────────

class SupabaseLoginMfaChallenge(BaseModel):
    status: str = "mfa_required"
    access_token: str # Il token AAL1 da usare per la verifica
    factor_id: str
    challenge_id: str

class SupabaseVerifyMfaInput(BaseModel):
    access_token: str
    factor_id: str
    challenge_id: str
    code: str = Field(..., description="Codice OTP (One-Time Password)")

class SupabaseVerifyMfaResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    user: Dict[str, Any]

class SupabaseTotpEnrollInput(BaseModel):
    friendly_name: Optional[str] = Field(None, description="Nome amichevole per il fattore MFA, es. 'Mio Telefono'")

class SupabaseTotpEnrollResponse(BaseModel):
    factor_id: str
    secret: str
    otpauth_uri: str
    qr_code: str # SVG string
    challenge_id: str

class SupabaseListFactorsResponse(BaseModel):
    factors: list[Dict[str, Any]]

class SupabaseMfaDisableInput(BaseModel):
    code: str = Field(..., description="Codice OTP (One-Time Password) per confermare la disattivazione")
