from typing import Optional
import datetime

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer

from src.config.config import settings
from src.db.models import User
from src.repositories.rp_users import oUsers



class Authorization:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth_scheme = OAuth2PasswordBearer('/auth/signup')

    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    

    # CREATE TOKEN
    async def create_token(self, data: dict, scope: str, exp_delta: Optional[float] = None):
        to_encode = data.copy()
        if exp_delta:
            expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=exp_delta)
        else:
            expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
        to_encode.update({"iat": datetime.datetime.now(datetime.UTC), "exp": expire, "scope": scope})
        encoded_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_token

    # DECODE TOKEN
    async def decode_token(self, token: str, scope: str) -> str:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == scope:
                email: Optional[str] = payload.get("sub")
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    # GET EMAIL FROM TOKEN
    async def get_email_from_token(self, token: str) -> str:
        try:
            if token is None or token == "":
                return None
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload.get("sub")
            return email
        except JWTError as e:
            return None
    
    # GET CURRENT USER
    async def get_current_user(self, token: str = Cookie(None, alias=settings.jwt_token)) -> Optional[User]:
        try:
            email = await self.decode_token(token, scope="refresh_token")
            user = await oUsers.get_data_by("email", email)

            if user:
                return user
            return None

        except Exception:
            return None
        

auth_service = Authorization()