import os
from pathlib import Path
from datetime import datetime

from utils.logger import get_logger


logger = get_logger(__name__)


S5_PATH = Path(os.path.realpath(__file__)).parent

files_path = S5_PATH / 'downloads'


# structure
#   company name : (creation date ISO-timestamp, full path)
last_files_path = {}


def get_last_files():
    with os.scandir(files_path) as it:
        logger.info(f"scanning '{files_path}' ...")
        json_count = 0
        for entry in it:
            if entry.is_file() and entry.name.endswith('.json'):
                json_count += 1
                name = entry.name.split('_')[0]
                datetime_timestamp = datetime.fromisoformat(entry.name.split('_')[1][:-5]
                                                   .replace("Z", "+00:00")).timestamp()
                full_path = entry.path
                if name not in last_files_path:
                    last_files_path.update({name : (datetime_timestamp, full_path)})
                else:
                    if datetime_timestamp > last_files_path[name][0]:
                        last_files_path[name] = (datetime_timestamp, full_path)
        logger.info(f"found {json_count} json files in '{files_path}' directory")
        logger.info(f"companies: {last_files_path.keys()}")

