#!/usr/bin/env python3
"""
ETL script to read raw Tweets CSV from MinIO (S3) and write an Iceberg table via PySpark.
"""
from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder \
        .appName('AirlineSentimentETL') \
        .config('spark.jars.packages', 'org.apache.iceberg:iceberg-spark3-runtime:1.3.0') \
        .config('spark.sql.catalog.spark_catalog', 'org.apache.iceberg.spark.SparkSessionCatalog') \
        .config('spark.sql.catalog.spark_catalog.type', 'hadoop') \
        .config('spark.sql.catalog.spark_catalog.warehouse', 's3a://iceberg-warehouse/') \
        .config('spark.hadoop.fs.s3a.endpoint', 'http://minio:9000') \
        .config('spark.hadoop.fs.s3a.access.key', 'minioadmin') \
        .config('spark.hadoop.fs.s3a.secret.key', 'minioadmin') \
        .config('spark.hadoop.fs.s3a.path.style.access', 'true') \
        .config('spark.hadoop.fs.s3a.connection.ssl.enabled', 'false') \
        .getOrCreate()

    # Read raw data
    df = spark.read.csv('s3a://raw/Tweets.csv', header=True, inferSchema=True)
    df.createOrReplaceTempView('tweets')

    # Create and populate Iceberg table
    spark.sql('CREATE DATABASE IF NOT EXISTS default')
    spark.sql(
        '''
        CREATE TABLE IF NOT EXISTS default.twitter_us_airline_sentiment
        USING iceberg
        AS SELECT * FROM tweets
        '''
    )
    spark.stop()

if __name__ == '__main__':
    main()