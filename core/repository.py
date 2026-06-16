from requests import session
from sqlalchemy import select
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

    def __init__(self, session: Session):
        self.session = session

    def load_course(self, course: Course) -> None:
        self.session.add(course)
        self.session.commit()