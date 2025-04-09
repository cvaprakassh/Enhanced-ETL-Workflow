import boto3
import pandas as pd
import io
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
import os
import logging
from _datetime import datetime


# Set up logging
log_file = f"/tmp/etl_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()

# Load environment variables from .env file
load_dotenv()

#print("Loaded S3 Bucket Name:", os.getenv("S3_BUCKET"))

logger.info("Starting data extraction from S3...")


s3 = boto3.client('s3')
bucket = os.getenv('S3_BUCKET')
prefix = 'raw/'

# List objects in the folder
objects = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

# Load files into DataFrames
dataframes = []

for obj in objects.get('Contents', []):
    key = obj['Key']
    if key.endswith('.csv'):
        response = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(io.BytesIO(response['Body'].read()))
        dataframes.append(df)
    elif key.endswith('.json'):
        response = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_json(io.BytesIO(response['Body'].read()), lines=True)
        dataframes.append(df)
    elif key.endswith('.xml'):
        response = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_xml(io.BytesIO(response['Body'].read()))
        dataframes.append(df)

# Combine all into one DataFrame
raw_data = pd.concat(dataframes, ignore_index=True)

logger.info("Extraction from S3 Completed..")

# Transformations

logger.info("Starting data transformation...")

# Inches to meters (e.g., height column)
if 'height_in' in raw_data.columns:
    raw_data['height_m'] = raw_data['height_in'] * 0.0254

# Pounds to kilograms (e.g., weight column)
if 'weight_lb' in raw_data.columns:
    raw_data['weight_kg'] = raw_data['weight_lb'] * 0.453592

# Drop duplicates
raw_data.drop_duplicates(inplace=True)

# Fill missing values
raw_data.fillna(method='ffill', inplace=True)

# Standardize column names
raw_data.columns = [col.strip().lower().replace(" ", "_") for col in raw_data.columns]


logger.info("Data transformation completed.")

logger.info(f"Saving transformed data to S3 ...")



# Save the transformed data to S3
output_buffer = io.StringIO()
raw_data.to_csv(output_buffer, index=False)
output_buffer.seek(0)   
try:
    s3.put_object(Bucket=bucket, Key='processed/transformed_data.csv', Body=output_buffer.getvalue())
    print("Data transformation complete and saved to S3.")
except Exception as e:
    print(f"Error saving transformed data to S3: {e}")


logger.info("Writing data to RDS usig SQLAlchemy connection...")


# Save to MySQL

# Define your connection details
username = os.getenv('RDS_USER')
password = os.getenv('RDS_PASS')
host = os.getenv('RDS_HOST')
port = os.getenv('RDS_PORT')
database = os.getenv('RDS_DB')

# create a SQLAlchemy engine
engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')

# Check if the database exists, if not create it
if not database_exists(engine.url):
    create_database(engine.url)
    print(f"Database {database} created.")

# Save the DataFrame to MySQL
try:
    raw_data.to_sql('transformed_data', con=engine, if_exists='replace', index=False)
    print("Data saved to MySQL database.")
except Exception as e:
    print(f"Error saving data to MySQL: {e}")
# Close the engine connection
engine.dispose()
logger.info("Data saved to MySQL database successfully.")
logger.info("ETL process completed successfully.")
logger.info(f"Log file: {log_file}")

try:
    log_s3_path = "my-etl-project-bucket-project/logs/"
    s3 = boto3.client("s3")
    s3.upload_file(log_file, "my-etl-project-bucket-project", f"logs/{os.path.basename(log_file)}")
    logger.info(f"Log file uploaded to S3: s3://{log_s3_path}{os.path.basename(log_file)}")
except Exception as e:
    logger.error(f"Failed to upload log to S3: {e}")

# Close the logger
logger.handlers[0].close()
logger.removeHandler(logger.handlers[0])

# Close the S3 client
s3.close()
