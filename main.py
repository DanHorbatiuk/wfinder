from core.db import reset_db
from fetch import get_data_from_resources
from storage.loader import process_pending_files


def run():
    get_data_from_resources()
    process_pending_files()

if __name__ == '__main__':
    run()
