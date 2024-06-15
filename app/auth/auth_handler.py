import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

import jwt
from decouple import config
from jose import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

JWT_SECRET="e260bab41ec5c816f90e681cebc4e661414c049bc7f5f7f8"
JWT_ALGORITHM ="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365 * 10

def token_response(token: str):
    return {
        "access_token": token
    }

# def sign_jwt(user_id: str) -> Dict[str, str]:
#     payload = {
#         "user_id": user_id,
#         "expires": time.time() + 600
#     }
#     token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

#     return token_response(token)

# def decode_jwt(token: str) -> dict:
#     try:
#         decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
#         return decoded_token if decoded_token["expires"] >= time.time() else None
#     except:
#         return {}
    
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# Function to verify the token remains unchanged
def verify_token(token: str, credentials_exception: HTTPException):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception