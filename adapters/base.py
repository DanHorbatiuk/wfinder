from abc import abstractmethod, ABC

from core.model import Course, FileRecord


class BaseAdapter(ABC):
    source: str

    @abstractmethod
    def parse(self, raw: dict, file_record_id: int) -> Course:
        """Перетворює один сирий запис у уніфікований Course"""
        pass