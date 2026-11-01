from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database import get_db
from app.config import settings
from app.models.user import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    if user is None or not user.is_active:

        raise HTTPException(
            status_code=401,
            detail="User not found or inactive"
        )

    return user


def require_role(*roles):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):

        if current_user.role not in roles:

            raise HTTPException(
                status_code=403,
                detail="You are not authorized"
            )

        return current_user

    return role_checker