from datetime import datetime

from airflow.sdk import dag, task


@dag(
    schedule="0 8 * * *",  # daily at 8:00 am
    start_date=datetime(2026, 6, 16),
    catchup=False,
)
def load_courses_pipeline_dag():

    @task
    def fetch_and_save_data():
        from fetch import get_data_from_resources
        get_data_from_resources()
        return True

    @task
    def load_all_to_db():
        from storage.loader import process_pending_files
        process_pending_files()
        return True

    fetch_task = fetch_and_save_data()
    load_task = load_all_to_db()

    _ = fetch_task >> load_task


load_courses_pipeline_dag()
