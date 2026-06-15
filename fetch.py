import os
from pathlib import Path
from datetime import datetime

import httpx
from curl_cffi import requests as cf_requests
from dotenv import load_dotenv

from save_files import save_to_minio
from utils.logger import get_logger


logger = get_logger(__name__)


load_dotenv()

PREFIX = "CAREERS_URL_"
urls = {
    key.removeprefix(PREFIX).lower(): value
    for key, value in os.environ.items()
    if key.startswith(PREFIX)
}

logger.info(f"file '.env' loaded, {len(urls)} company founded")


S5_PATH = Path(os.path.realpath(__file__)).parent

write_path = S5_PATH / 'downloads'


def load_jsons():
    logger.info("start fetching resources...")
    for name, url in urls.items():
        try:
            logger.info(f"fetching {name} url...")
            response = cf_requests.get(
                url,
                headers={
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "en-US,en;q=0.5",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                },
            )
            response.raise_for_status()
            logger.info(f"fetching {name} finished")

            logger.debug(response.text)
            logger.info(f"writing to {write_path}/{name}_DATETIME.json...")
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            file = f"{name}_{timestamp}"

            # TEST LOCALLY
            # file = file + ".json"
            # with open(write_path / file, "w") as f:
            #     f.write(response.text)

            # ORIGINAL: SAVE TO MINIOBUCKET
            save_to_minio(file, response.text)

            logger.info(f"writing to {file} finished")
            logger.info("fetching finished successfully")

        except httpx.HTTPStatusError as e:
            logger.error(f"Error fetching {name}: {e}")
            continue
        except httpx.RequestError as e:
            logger.error("Network error:", str(e))
        except Exception as e:
            logger.error(f"Unknown error (fetch): {e}")