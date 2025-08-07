
# Import async SQLAlchemy components
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String

##############################################################
          # Database URL and Async Engine Setup #
##############################################################

# SQLite database using the aiosqlite driver for async support
DATABASE_URL = "sqlite+aiosqlite:///./requests.db"

# Create an asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,              
    class_=AsyncSession,      
    expire_on_commit=False  
)


##############################################################
                  # Request Log Table #
##############################################################

# Base class for all ORM models
Base = declarative_base()

# Table to store logs of each operation
class requests_log(Base):
    __tablename__ = "requests_log"  

    id = Column(Integer, primary_key=True, index=True)  
    operation = Column(String, index=True)             
    input = Column(String)                              
    result = Column(String)                           
