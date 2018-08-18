FROM python:3.6.6-stretch

LABEL maintainer="Aly Sivji <alysivji@gmail.com>" \
    description="Development image for Airflow practice project"

ENV AIRFLOW_HOME /usr/local/airflow

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ARG AIRFLOW__CORE__SQL_ALCHEMY_CONN
COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

COPY scripts/entrypoint.sh /entrypoint.sh
COPY scripts/check_postgres.py ${AIRFLOW_HOME}/check_postgres.py
COPY scripts/check_postgres.py ${AIRFLOW_HOME}/check_redis.py

RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow

RUN chown -R airflow: ${AIRFLOW_HOME} && \
    mkdir -p /tmp/work/ && \
    chown -R alysivji: /tmp/work && \
    chmod 755 /entrypoint.sh

EXPOSE 8080 8793

USER alysivji
WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT [ "/entrypoint.sh" ]
