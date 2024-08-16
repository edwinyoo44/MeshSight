from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import scoped_session, sessionmaker
from utils.ConfigUtil import ConfigUtil

# 設定檔讀取
config = ConfigUtil.read_config()
db_config = config["postgres"]
Engine = create_engine(
    f"postgresql+psycopg2://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}",
)

EngineAsync = create_async_engine(
    f"postgresql+asyncpg://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}",
    future=True,
)

SessionLocal = sessionmaker(Engine, autocommit=False, autoflush=False)
SessionLocalAsync = async_sessionmaker(EngineAsync, autocommit=False, autoflush=False)


def get_db_connection():
    db = scoped_session(SessionLocal)
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


async def get_db_connection_async() -> AsyncSession:
    try:
        async with SessionLocalAsync() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()
