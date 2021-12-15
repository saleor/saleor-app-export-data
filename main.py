import uvicorn
from saleor_app_base.core.app_settings import app_settings
from saleor_app_base.main import configure_application
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.export.products.api import router as products_router

app = configure_application()
app.include_router(products_router)


async def get_db() -> AsyncSession:
    """
    Dependency function that yields db sessions
    """
    async with async_session() as session:
        yield session
        await session.commit()


engine = create_async_engine(app_settings.SQLALCHEMY_DB_URI)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

if __name__ == "__main__":
    uvicorn.run(app, port=5000)
