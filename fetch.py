import os
from pathlib import Path
from datetime import datetime

from anyio.streams import file
from botocore.exceptions import ClientError
from curl_cffi import requests as cf_requests

from storage.loader import save_file_record
from storage.minio import save_object
from utils.logger import get_logger


logger = get_logger(__name__)


S5_PATH = Path(os.path.realpath(__file__)).parent

write_path = S5_PATH / 'downloads'


def fetch_and_save_single(name: str, url: str) -> dict:
    logger.info(f"fetching {name} url...")
    try:
        response = cf_requests.get(
            url,
            headers={
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-US,en;q=0.5",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            },
            timeout=15,
        )
        response.raise_for_status()
        logger.info(f"fetching {name} finished")

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        file_name = f"{name}_{timestamp}"
        load_file_and_meta(file_name, response.text)
        logger.info(f"file and meta {file_name} finished successfully")
        return {"name": name, "status": "success"}

    except Exception as e:
        logger.error(f"error fetching {name}: {e}")
        return {"name": name, "status": "error", "error": str(e)}


def load_file_and_meta(f_name, content):
    try:
        logger.info(f"loading file {f_name} to minio bucket...")
        meta = save_object(f_name, content)
        logger.info(f"file {f_name} saved to minio bucket")
        logger.debug(meta)
        logger.info(f"saving file {f_name} metadata to database...")
        save_file_record(
            bucket=meta["bucket"],
            key=meta["key"],
            source=f_name.split("_")[0],
            etag=meta["etag"],
            size_bytes=meta["size_bytes"],
        )
        logger.info(f"file metadata {f_name} saved to database")
    except ClientError as e:
        logger.error(f"error saving {file}: {e}")