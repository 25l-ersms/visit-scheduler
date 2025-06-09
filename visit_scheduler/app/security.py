# auth.py
import os
import traceback
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Cookie, HTTPException
from jose import ExpiredSignatureError, JWTError, jwt

from visit_scheduler.app.models.models import UserSessionData
from visit_scheduler.package_utils.logger_conf import logger

# Load environment variables
load_dotenv(override=True)

# JWT Configurations
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Cookie(None, alias="access_token")) -> UserSessionData:
    # return UserSessionData(user_id="1", user_email="test@test.com") # TODO: remove

    if not token:
        logger.error("No access_token cookie found")
        raise HTTPException(status_code=401, detail="Not authenticated")

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("sub")
        user_email: str = payload.get("email")

        if user_id is None or user_email is None:
            raise credentials_exception

        return UserSessionData(user_id=user_id, user_email=user_email, cookie_token=token)

    except ExpiredSignatureError:
        # Specifically handle expired tokens
        traceback.print_exc()
        raise HTTPException(status_code=401, detail="Session expired. Please login again.")
    except JWTError:
        # Handle other JWT-related errors
        traceback.print_exc()
        raise credentials_exception
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=401, detail="Not Authenticated")
