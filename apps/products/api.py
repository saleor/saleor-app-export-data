from fastapi import FastAPI, Depends
from databases import Database
from saleor_app_base.database import get_db
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select

from ..common.models import ExportFile, ExportFileTypesEnum
from .tasks import export_products_task

app = FastAPI()


@app.post("/export/products/")
async def export_products(
    db: Database = Depends(get_db),
):
    values = {"type": ExportFileTypesEnum.PRODUCTS.value()}
    file = await db.fetch_one(
        query=insert(ExportFile.__table__)
        .values(**values)
        .returning(ExportFile.__table__)
    )
    export_products_task.delay(file.id)
    return {"status": "ok"}


@app.get("/export/products/file/{file_id}/")
async def get_export_file(
    file_id: int,
    db: Database = Depends(get_db),
):
    file = await db.fetch_one(
        query=select(ExportFile.__table__)
        .where(ExportFile.id == file_id)
        .returning(ExportFile.__table__)
    )

    return {"status": "ok", "file": file.content_file}
