from typing import Dict, Optional, Tuple

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from database import get_db
from models.app_key import AppKey
from schemas.auth_schema import TokenPayload
from settings import settings

SYMMETRIC_ALG = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

app_audience: Optional[str] = settings.API_V1_STR or "rafiki-ase"


def _decode_user_token(token: str) -> Dict:
    """Decode HS256 user tokens signed with the shared secret."""
    return jwt.decode(
        token,
        settings.authjwt_secret_key,
        algorithms=[SYMMETRIC_ALG],
        options={"verify_aud": False},
    )


def _decode_app_token(db: Session, token: str, header: Dict) -> Tuple[Dict, Optional[AppKey]]:
    """Decode HS256 third-party tokens using per-app secrets stored in DB."""
    key_id = header.get("kid")
    if not key_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unknown or missing key id"
        )

    db_key = (
        db.query(AppKey)
        .filter(AppKey.id == key_id)
        .filter(AppKey.is_active.is_(True))
        .first()
    )

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unknown key id"
        )

    audience = db_key.audience if db_key.audience else app_audience

    return (
        jwt.decode(
            token,
            db_key.secret_key,
            algorithms=[SYMMETRIC_ALG],
            audience=audience if audience else None,
            options={"verify_aud": bool(audience)},
        ),
        db_key,
    )


def validate_auth(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> TokenPayload:
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg")

        if alg == SYMMETRIC_ALG:
            # Prefer per-app secret if kid present; otherwise fallback to user secret
            if header.get("kid"):
                payload, db_key = _decode_app_token(db, token, header)
            else:
                payload = _decode_user_token(token)
                db_key = None
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unsupported signing algorithm",
            )

        token_data = TokenPayload(**payload)

        if token_data.token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type",
            )

        if header.get("kid"):
            issuer_valid = True
            if db_key and db_key.issuer:
                issuer_valid = token_data.iss == db_key.issuer

            if not issuer_valid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid issuer for third-party token",
                )

            expected_audience = db_key.audience if db_key and db_key.audience else app_audience
            if expected_audience and token_data.aud and token_data.aud != expected_audience:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid audience for third-party token",
                )
    except (JWTError, ValidationError) as error:
        if isinstance(error, ValidationError):
            err_detail = error.errors()  # o e.json()
        else:  # JWTError
            err_detail = str(error) or repr(error)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Could not validate credentials",
                "error": err_detail,
            },
        )
    return token_data
