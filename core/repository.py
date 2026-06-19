from datetime import datetime, time

from sqlalchemy import select, inspect
from sqlalchemy.orm import Session

from core.model import FileRecord, Course


class FileRecordRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    """
        Source types (in current version):
            - epam
            - softserve
        Status types:
            - pending
            - processing
            - done/error
    """
    def get_records_by_status(self, status: str) -> list[FileRecord]:
        stmt = select(FileRecord).where(FileRecord.status == status)
        return list(self.session.scalars(stmt))



class CourseRepository:


    EXCLUDED_FIELDS = {"id", "source", "source_id", "created_at", "active_from", "active_to",
                       "file_record_id"}


    def __init__(self, session: Session):
        self.session = session


    def upsert_course(self, course: Course) -> None:
        existing = (
            self.session.query(Course)
            .filter(
                Course.source == course.source,
                Course.source_id == course.source_id,
                Course.active_to.is_(None), # is active
            )
            .one_or_none()
        )
        now = datetime.utcnow()
        course.active_from = now
        if existing is not None:
            existing.active_to = now
        self.session.add(course)


    def get_courses_created_today(self) -> list[Course]:
        today_start = datetime.combine(datetime.utcnow().date(), time.min)
        stmt = select(Course).where(
            Course.created_at >= today_start,
            Course.active_to.is_(None),
        )
        return list(self.session.scalars(stmt))