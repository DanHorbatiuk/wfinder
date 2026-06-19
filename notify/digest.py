from core.db import Session
from core.repository import CourseRepository
from notify.telegram import send_telegram_message
from utils.logger import get_logger

logger = get_logger(__name__)


def build_and_send_today_digest() -> None:
    session = Session()
    try:
        repo = CourseRepository(session)
        courses = repo.get_courses_created_today()

        if not courses:
            send_telegram_message("Сьогодні нових курсів немає.")
            return

        lines = [f"🆕 Курси за сьогодні: {len(courses)}\n"]
        for c in courses:
            free_label = "🆓" if c.price == "Free" else "💰"
            lines.append(f"{free_label} <b>{c.title}</b> ({c.source})")

        send_telegram_message("\n".join(lines))
        logger.info(f"digest sent: {len(courses)} courses")
    finally:
        session.close()