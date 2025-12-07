from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from settings import settings

# URL de conexión a la base de datos
DATABASE_URL = settings.database_uri

# Crear el engine
engine = create_engine(DATABASE_URL)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

config_elastic = {
    'url': settings.ELASTIC_URL,
    'user': 'elastic',
    'password': settings.ELASTIC_PASSWORD,
    'index': settings.ELASTIC_INDEX,
    'environment':settings.ELASTIC_ENVIRONMENT,
    'limit': False,
    'debug': False
}
