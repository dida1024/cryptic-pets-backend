from sqlmodel import SQLModel, create_engine

from infrastructure.config import settings

from .models import *  # noqa: F403

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True, future=True)

def init_db():
    SQLModel.metadata.create_all(engine)
