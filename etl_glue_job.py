import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col
import boto3
import os

# Get job arguments
args = getResolvedOptions(sys.argv, ['Etlflow'])


# Initialize Glue Context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['Etlflow'], args)

# Load data from S3
s3_path = "s3://my-etl-project-bucket-project/raw/"

df_csv = spark.read.option("header", "true").csv(s3_path + "*.csv")
df_json = spark.read.option("multiline", "true").json(s3_path + "*.json")
df_xml = spark.read.format("xml").option("rowTag", "record").load(s3_path + "*.xml")

# Combine all DataFrames
df = df_csv.unionByName(df_json, allowMissingColumns=True).unionByName(df_xml, allowMissingColumns=True)

# Transformations
df = df.select([col(column).alias(column.strip().lower().replace(" ", "_")) for column in df.columns])

if 'height_in' in df.columns:
    df = df.withColumn('height_m', col('height_in') * 0.0254)

if 'weight_lb' in df.columns:
    df = df.withColumn('weight_kg', col('weight_lb') * 0.453592)

df = df.dropDuplicates()
fill_dict = {}

if 'height_m' in df.columns:
    fill_dict['height_m'] = 0

if 'weight_kg' in df.columns:
    fill_dict['weight_kg'] = 0

if fill_dict:
    df = df.na.fill(fill_dict)


# Save to S3
output_path = "s3://my-etl-project-bucket-project/transformed/"
df.write.mode("overwrite").option("header", "true").csv(output_path + "transformed_data")

# Initialize AWS Glue Context
client = boto3.client("glue")
conn = client.get_connection(Name="rds_mysql_connection")["Connection"]

conn_props = conn['ConnectionProperties']
jdbc_url = conn_props["JDBC_CONNECTION_URL"]
user = conn_props["USERNAME"]
password = conn_props["PASSWORD"]

# Save to RDS using Glue Connection
df.write \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("user", user) \
    .option("password", password) \
    .option("dbtable", "transformed_data") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .mode("overwrite") \
    .save()


# Finalize job
job.commit()
