from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    project_name: str = 'routing'
    postgres_password: str = '123qwe'
    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_db: str = 'users'
    postgres_user: str = 'postgres'
    postgres_scheme: str = 'postgresql+asyncpg'

    @property
    def postgres_dsn(self):
        return (
            f'{self.postgres_scheme}://{self.postgres_user}:{self.postgres_password}@'
            f'{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
        )

    model_config = ConfigDict(env_file='.env', extra='ignore')



settings = Settings()
