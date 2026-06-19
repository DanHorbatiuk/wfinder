from core.db import Session
from core.repository import CourseRepository
from notify.telegram import send_telegram_message
from utils.logger import get_logger

logger = get_logger(__name__)


def notify_new_courses() -> None:
    session = Session()
    try:
        repo = CourseRepository(session)
        courses = repo.get_courses_created_today()

        if not courses:
            logger.info("no new courses today, skipping notification")
            return

        lines = [f"🆕 Нові курси сьогодні: {len(courses)}\n"]
        for course in courses:
            free_label = "🆓" if course.price == "Free" else "💰"
            lines.append(
                f"{free_label} <b>{course.title}</b>\n"
                f"   {course.source} | {course.direction or '-'} | {course.level or '-'}"
            )

        send_telegram_message("\n".join(lines))
        logger.info(f"notified about {len(courses)} new courses")
    finally:
        session.close()

notify_new_courses()