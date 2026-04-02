
import os
from starlette.config import Config

config = Config(".env")

# JWT
JWT_SECRET: str = config("JWT_SECRET")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRY_HOURS: int = 24
JWT_ACCESS_EXPIRY_SECONDS: int = 60 * 15 # 15 minutes
JWT_REFRESH_EXPIRY_SECONDS: int = 3600 * 24 * 7 # 7 days

# Judge Server
JUDGE_SERVER_URL: str = config("JUDGE_SERVER_URL", default="http://judge:5050")

# Database
SQLALCHEMY_DATABASE_URI: str = config("SQLALCHEMY_DATABASE_URI")



# Storage
PROBLEMS_STORAGE_PATH: str = config("PROBLEMS_STORAGE_PATH", default="./problems_storage")

# RabbitMQ server
CLOUDAMQP_URL: str = config("CLOUDAMQP_URL", default="")