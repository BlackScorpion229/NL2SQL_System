"""JWT authentication and authorization utilities."""
from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from loguru import logger
from app.config import settings

# HTTP Bearer security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    FastAPI dependency to validate JWT and extract user context.

    Args:
        credentials: HTTP Authorization header credentials

    Returns:
        Dict containing user_id and role

    Raises:
        HTTPException: If token is invalid, expired, or role is invalid
    """
    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        logger.debug("JWT token decoded successfully")

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed token",
        )
    except Exception as e:
        logger.error(f"Unexpected error decoding JWT: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )

    # Extract user information
    user_id = payload.get("sub")
    role = payload.get("role")

    # Validate role
    if role not in ("admin", "viewer"):
        logger.warning(f"Invalid role in token: {role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role",
        )

    if not user_id:
        logger.warning("Missing user_id in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID missing from token",
        )

    user_context = {
        "user_id": user_id,
        "role": role,
    }

    logger.info(f"Authenticated user {user_id} with role {role}")
    return user_context


def create_jwt_token(user_id: str, role: str) -> str:
    """
    Create a JWT token for a user.

    Args:
        user_id: Unique user identifier
        role: User role ('admin' or 'viewer')

    Returns:
        Signed JWT token string
    """
    import datetime

    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token
