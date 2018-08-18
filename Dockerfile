FROM python:3.6.6-stretch

LABEL maintainer="Aly Sivji <alysivji@gmail.com>" \
    description="Development image for Airflow practice project"

# Never prompts the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Airflow
ARG AIRFLOW_VERSION=1.9.0
ARG AIRFLOW_HOME=/usr/local/airflow

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ARG AIRFLOW__CORE__SQL_ALCHEMY_CONN
COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

COPY scripts/entrypoint.sh /entrypoint.sh
COPY scripts/check_postgres.py ${AIRFLOW_HOME}/check_postgres.py
COPY scripts/check_redis.py ${AIRFLOW_HOME}/check_redis.py

RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow && \
    chown -R airflow: ${AIRFLOW_HOME} && \
    mkdir -p /tmp/work/ && \
    chown -R airflow: /tmp/work && \
    chmod 755 /entrypoint.sh

EXPOSE 8080 8793

USER airflow
WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "webserver" ]
