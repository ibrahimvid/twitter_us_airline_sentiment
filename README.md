# Twitter US Airline Sentiment Datalake Project

An end-to-end data pipeline for processing and analyzing US airline sentiment using:
- Apache Airflow for orchestration
- PySpark for ETL and Apache Iceberg for table management
- MinIO as an S3-compatible data lake storage
- Trino for interactive SQL analytics

## Prerequisites
- Docker & Docker Compose
- Kaggle API token file (`kaggle.json`) in the project root

## Project Structure
```
.
├── docker-compose.yml
├── kaggle.json                # Your Kaggle credentials
├── airflow/
│   ├── Dockerfile            # Custom Airflow image (Java + Python deps)
│   ├── requirements.txt      # Python dependencies for Airflow
│   ├── dags/
│   │   └── twitter_airline_sentiment_dag.py
│   └── scripts/
│       └── etl.py            # PySpark ETL script
└── trino/
    └── etc/
        └── catalog/
            └── iceberg.properties
```

## Setup & Run
1. Place your Kaggle API token file as `kaggle.json` in the project root.
2. Start services:
   ```bash
   docker-compose up -d
   ```
3. Create MinIO buckets:
   ```bash
   # Install mc (MinIO client) or use the web UI
   docker exec -it minio sh -c \
     "mc alias set local http://localhost:9000 minioadmin minioadmin && \
      mc mb local/raw && mc mb local/iceberg-warehouse"
   ```
4. Access the Airflow UI at http://localhost:8080 and trigger the `twitter_airline_sentiment` DAG.
5. After ETL succeeds, connect to Trino for interactive queries:
   ```bash
   docker exec -it trino trino --server trino:8080 --catalog iceberg --schema default
   trino> SHOW TABLES;
   trino> SELECT airline, count(*) AS cnt FROM default.twitter_us_airline_sentiment GROUP BY airline;
   ```

## Next Steps
- Add scheduling and parameterize DAG for incremental loads
- Implement data quality checks (e.g. with Great Expectations)
- Add monitoring/alerting (e.g. via Slack notifications)
- Containerize and scale PySpark jobs separately