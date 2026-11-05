import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import sqlalchemy
import dotenv

# loading dotev
dotenv.load_dotenv()

database_url= os.environ.get('DB_PATH')

if not database_url:
    raise ValueError("ERROR: Could not connect to DB. Try again!!!")

metadata= sqlalchemy.MetaData()
engine= create_engine(database_url, echo=False, pool_pre_ping=True, 
                      pool_recycle= 3600, pool_size= 20, max_overflow= 0)
LocalSession= sessionmaker(bind= engine, autoflush= False, autocommit= False)


class Base(DeclarativeBase):
    pass


# openning and closing connection with DB
def get_db():    
    db = LocalSession()

    try:
        yield db
    finally:
        db.close()