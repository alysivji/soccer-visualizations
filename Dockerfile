FROM python:3.6.6-stretch

LABEL maintainer="Aly Sivji <alysivji@gmail.com>" \
    description="Development image for Airflow practice project"

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ARG AIRFLOW__CORE__SQL_ALCHEMY_CONN
ARG AIRFLOW__CORE__EXECUTOR
ENV AIRFLOW_HOME /usr/local/airflow

EXPOSE 8080
WORKDIR ${AIRFLOW_HOME}

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
