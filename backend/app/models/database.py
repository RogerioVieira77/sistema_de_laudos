"""
Base Database Configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Database Configuration using environment variables
db_user = os.getenv("DB_USER", "dbadmin_dev")
db_password = os.getenv("DB_PASSWORD", "Dev@)((42))")
db_host = os.getenv("DB_HOST", "postgres")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "sistema_de_laudos_dev")

# URL-encode the password to handle special characters
db_password_encoded = quote_plus(db_password)
DATABASE_URL = f"postgresql://{db_user}:{db_password_encoded}@{db_host}:{db_port}/{db_name}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

# SessionLocal for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
