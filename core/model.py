from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column


class Base(DeclarativeBase):
    pass


class FileRecord(Base):
    __tablename__ = "file_record"
    id: Mapped[int] = mapped_column(primary_key=True)
    bucket: Mapped[str]
    key: Mapped[str] = mapped_column(unique=True)
    etag: Mapped[str]
    source: Mapped[str] # "epam" | "softserve" | "sigma"
    status: Mapped[str] = mapped_column(default="pending") # pending → processing → done/error
    size_bytes: Mapped[int | None]
    uploaded_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    processed_at: Mapped[datetime | None]
    error_message: Mapped[str | None]

    courses: Mapped[list["Course"]] = relationship(
        back_populates="file_record",
        cascade="all, delete-orphan" # каскадне видалення
    )

    def __repr__(self) -> str:
        return f"FileRecord(id={self.id}, bucket={self.bucket}, key={self.key})"


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_course_source_id"),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str]  # "epam" | "softserve" | "sigma"
    source_id: Mapped[str]       # original id from source (str to cover all cases)
    title: Mapped[str]
    url: Mapped[str | None] = mapped_column(unique=True)
    course_type: Mapped[str | None]   # "Training", "Internship", "Course"
    direction: Mapped[str | None]     # "DevOps", "CloudAndDevOps", "QA"
    format: Mapped[str | None]        # "Online", "Offline"
    level: Mapped[str | None]         # "Junior", "Middle", "Specialization"
    is_free: Mapped[bool] = mapped_column(default=False)
    price: Mapped[str | None]         # "Free" or actual price string
    date_start: Mapped[datetime | None]
    date_end: Mapped[datetime | None]
    status: Mapped[str | None]        # "Open for Registration", "RegistrationOpen"
    is_expired: Mapped[bool] = mapped_column(default=False)
    country: Mapped[str | None]
    city: Mapped[str | None]
    languages: Mapped[list | None] = mapped_column(JSONB)  # ["English", "Ukrainian"]

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    file_record_id: Mapped[int] = mapped_column(ForeignKey("file_record.id"))
    file_record: Mapped["FileRecord"] = relationship(back_populates="courses")

    def __repr__(self) -> str:
        return (
            f"Course(id={self.id}/{self.source_id}, source={self.source!r}, "
            f"title={self.title!r}, type={self.course_type!r}, "
            f"status={self.status!r}, is_free={self.is_free})"
        )