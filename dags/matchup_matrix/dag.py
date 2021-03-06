from datetime import timedelta

import airflow
from airflow.operators import BashOperator, PythonOperator
from airflow.models import DAG

from matchup_matrix.tidy_results_dataset import transform_results_data
from matchup_matrix.generate_matchup_matrix import create_match_matrix

default_args = {
    "owner": "sivpack",
    "start_date": airflow.utils.dates.days_ago(2),
    "email": ["alysivji@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(dag_id="matchup_matrix", default_args=default_args, schedule_interval=None)

# Download csv
download_results = BashOperator(
    task_id="download_results_dataset",
    bash_command="curl http://www.football-data.co.uk/mmz4281/1819/E0.csv -o /tmp/work/premier_league.csv",
    dag=dag,
)

# Clean data
op_kwargs = {}  # TODO: use this for when we are creating for multiple leagues
transform_results = PythonOperator(
    task_id="transform_results_dataset",
    provide_context=True,
    op_kwargs=op_kwargs,
    python_callable=transform_results_data,
    dag=dag,
)

# Visualization
op_kwargs = {}
matchup_matrix = PythonOperator(
    task_id="create_match_matrix",
    provide_context=True,
    op_kwargs=op_kwargs,
    python_callable=create_match_matrix,
    dag=dag,
)

download_results >> transform_results >> matchup_matrix
