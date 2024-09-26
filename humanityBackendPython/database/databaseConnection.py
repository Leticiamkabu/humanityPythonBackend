import os


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession 
from sqlalchemy.orm import sessionmaker, DeclarativeBase

db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')



SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}/{db_name}"  


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo = True ) 


SessionLocal = sessionmaker(expire_on_commit = False, class_=AsyncSession, bind = engine) 

class Base(DeclarativeBase):
    pass



async def create_database_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        

# Use asyncio to run the asynchronous setup code
async def setup():
    await create_database_tables()