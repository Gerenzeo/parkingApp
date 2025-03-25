import os

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()

class Settings(BaseModel):
    
    # PostgreSQL
    postgres_user: str = os.getenv("POSTGRES_USERNAME", "username")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "**********")
    postgres_domain: str = os.getenv("POSTGRES_DOMAIN", "localhost")
    postgres_port: int = os.getenv("POSTGRES_PORT", 5432)
    postgres_db_name: str = os.getenv("POSTGRES_DBNAME", "databasename")


    # Cloudinary
    cloudinary_name: str = os.getenv("CLOUDINARY_NAME", "folder")
    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY", "API key")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET", "#########")


    # SYSTEM
    secret_key: str = os.getenv("SECRET_KEY", "secret_key")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    jwt_token: str = os.getenv("JWTOKEN", "")
    refresh_token_time: int = os.getenv("REFRESH_TOKEN", 3000)

    # GMAIL
    gmail_sender: str = os.getenv("GMAIL_SENDER", "mail")
    gmail_password: str = os.getenv("GMAIL_PASSWORD", "*******")


    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    @property
    def sqlalchemy_postgresql_database_url(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_domain}:{self.postgres_port}/{self.postgres_db_name}"
    


settings = Settings()