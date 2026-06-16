from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.model import Base
from core.setting import get_settings


engine = create_engine(get_settings().postgres_url)
Session = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)