import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .setting import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)