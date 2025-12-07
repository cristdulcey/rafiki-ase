from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from database import get_db
from schemas.auth_schema import TokenPayload
from settings import settings
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def validate_auth(
        db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.authjwt_secret_key, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_data
