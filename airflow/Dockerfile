FROM apache/airflow:2.7.1-python3.11
USER root
# Install Java runtime for Spark
RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    rm -rf /var/lib/apt/lists/*
# Prepare Kaggle config directory
RUN mkdir -p /opt/airflow/.kaggle && chown -R airflow: /opt/airflow/.kaggle
# Install required Python packages as the 'airflow' user
COPY requirements.txt /requirements.txt
USER airflow
RUN pip install --no-cache-dir -r /requirements.txt
WORKDIR /opt/airflow