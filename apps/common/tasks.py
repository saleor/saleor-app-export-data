from sqlalchemy import update
from saleor_app_base.database import get_db

from . import events
from .models import ExportFile, JobStatusesEnum
from .notifications import send_export_failed_info


def on_task_failure(self, exc, task_id, args, kwargs, einfo):
    export_file_id = args[0]

    db = get_db()
    export_file = db.fetch_one(
        query=update(ExportFile.__table__)
        .where(ExportFile.id == export_file_id)
        .values(content_file=None, status=JobStatusesEnum.FAILED.value())
    )

    events.export_failed_event(
        export_file=export_file,
        message=str(exc),
        error_type=str(einfo.type),
    )

    send_export_failed_info(export_file)


def on_task_success(self, retval, task_id, args, kwargs):
    export_file_id = args[0]

    db = get_db()
    export_file = db.fetch_one(
        query=update(ExportFile.__table__)
        .where(ExportFile.id == export_file_id)
        .values(content_file=None, status=JobStatusesEnum.SUCCESS.value())
    )

    events.export_success_event(
        export_file=export_file,
    )
