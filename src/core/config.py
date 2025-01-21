import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Config:
    """Application configuration settings."""
    
    database_url: str = os.getenv('DATABASE_URL', 'postgresql://test:test@localhost:5432/test_db')
    mongodb_url: str = os.getenv('MONGODB_URL', 'mongodb://test:test@localhost:27017/test_db')
    secret_key: str = os.getenv('SECRET_KEY', 'dev')
    debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    testing: bool = os.getenv('TESTING', 'False').lower() == 'true'
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.database_url:
            raise ValueError("DATABASE_URL must be set")
        if not self.mongodb_url:
            raise ValueError("MONGODB_URL must be set")
        if not self.secret_key:
            raise ValueError("SECRET_KEY must be set")
        
        # Validate URLs
        if not self.database_url.startswith('postgresql://'):
            raise ValueError("DATABASE_URL must be a PostgreSQL URL")
        if not self.mongodb_url.startswith('mongodb://'):
            raise ValueError("MONGODB_URL must be a MongoDB URL")

    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        return cls()

    def as_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'DATABASE_URL': self.database_url,
            'MONGODB_URL': self.mongodb_url,
            'SECRET_KEY': self.secret_key,
            'DEBUG': self.debug,
            'TESTING': self.testing
        }