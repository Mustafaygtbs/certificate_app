from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import config

Base = declarative_base()

def get_engine():
    """Veritabanı motoru oluştur"""
    return create_engine(config.DATABASE_URL)

def get_session():
    """Veritabanı oturumu başlat"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    """Veritabanını oluştur"""
    engine = get_engine()
    Base.metadata.create_all(engine)
