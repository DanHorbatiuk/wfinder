import json
import logging

import boto3

from adapters.epam import EpamAdapter
from adapters.softserve import SoftServeAdapter
from core.db import Session
from core.model import FileRecord
from core.repository import CourseRepository, FileRecordRepository
from storage.minio import get_s3_client

logger = logging.getLogger(__name__)


ADAPTERS = {
    "epam": EpamAdapter(),
    "softserve": SoftServeAdapter(),
}


"""
    Get file from MinIO
    Change json --> Course
    Load Course obj in DB
"""
def process_one_file(
        file_record: FileRecord,
        file_repo: FileRecordRepository,
        course_repository: CourseRepository
) -> None:
    logger.info(f"processing file {file_record.key}...")
    s3_client = get_s3_client()
    file_record.status = "processing"
    file_repo.session.commit()
    response = s3_client.get_object(
        Bucket=file_record.bucket,
        Key=file_record.key
    )
    content = response["Body"].read()
    raw_data = json.loads(content)
    logger.info(f"file {file_record.key} loaded")
    adapter = ADAPTERS.get(file_record.source)
    if adapter is None:
        file_record.status = "error"
        file_record.error_message = "unknown source"
        file_repo.session.commit()
        logger.info(f"error processing file {file_record.key}: {file_record.error_message}")
        logger.info(f"unknown source: {file_record.source}")
        return
    logger.info(f"file source is {file_record.source}")
    courses = adapter.parse(raw_data, file_record.id)
    logger.info(f"file transformed in Course record")
    for course in courses:
        course_repository.upsert_course(course)
    file_record.status = "done"
    file_repo.session.commit()
    logger.info(f"file '{file_record.key}' processed, total: {len(courses)} courses")


def process_pending_files() -> None:
    session = Session()
    course_repo = CourseRepository(session)
    file_repo = FileRecordRepository(session)
    logger.info("processing pending files...")
    files_records = file_repo.get_records_by_status("pending")
    logger.info(f"{len(files_records)} pending files to process founded")
    for file_record in files_records:
        process_one_file(file_record, file_repo, course_repo)
    logger.info(f"pending files processed successfully, total file: {len(files_records)}")
    session.close()


def save_file_record(
    bucket: str,
    key: str,
    etag: str,
    source: str,
    size_bytes: int,
) -> FileRecord:
    session = Session()
    try:
        file_record = FileRecord(
            bucket=bucket,
            key=key,
            etag=etag,
            source=source,
            size_bytes=size_bytes,
        )
        session.add(file_record)
        session.commit()
        return file_record
    finally:
        session.close()


