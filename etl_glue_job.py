import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col
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
df = df.na.fill(method='ffill')  # Proper way to use fillna with PySpark

# Save to S3
output_path = "s3://my-etl-project-bucket-project/transformed/"
df.write.mode("overwrite").option("header", "true").csv(output_path + "transformed_data.csv")

# Save to RDS using Glue Connection
df.write \
    .format("jdbc") \
    .option("dbtable", "transformed_data") \
    .option("connectionName", "rds_mysql_connection") \
    .option("useConnectionProperties", "true") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .mode("overwrite") \
    .save()

# Finalize job
job.commit()
