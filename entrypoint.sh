#!/bin/bash

case $1 in
    airflow)
        case $2 in
            webserver)
                airflow initdb
                airflow webserver
                ;;
            scheduler)
                airflow scheduler
                ;;
            *)
                printf $"Usage: $1 {webserver | scheduler} \n"
        esac
        ;;
    *)
        printf $"Usage: $0 {airflow} \n"
        exit 1
        ;;
esac
