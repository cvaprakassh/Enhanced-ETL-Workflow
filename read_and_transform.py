import boto3
import pandas as pd
import io
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

s3 = boto3.client('s3')
bucket = os.getenv('S3_BUCKET_NAME')
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
        df = pd.read_json(io.BytesIO(response['Body'].read()))
        dataframes.append(df)
    elif key.endswith('.xml'):
        response = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_xml(io.BytesIO(response['Body'].read()))
        dataframes.append(df)

# Combine all into one DataFrame
raw_data = pd.concat(dataframes, ignore_index=True)

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

# Save the transformed data to S3
output_buffer = io.StringIO()
raw_data.to_csv(output_buffer, index=False)
output_buffer.seek(0)   
try:
    s3.put_object(Bucket=bucket, Key='processed/transformed_data.csv', Body=output_buffer.getvalue())
    print("Data transformation complete and saved to S3.")
except Exception as e:
    print(f"Error saving transformed data to S3: {e}")

# Save to MySQL

# Define your connection details
username = os.getenv('RDS_USERNAME')
password = os.getenv('RDS_PASSWORD')
host = os.getenv('RDS_HOSTNAME')
port = os.getenv('RDS_PORT')
database = os.getenv('RDS_DB_NAME')

# create a SQLAlchemy engine
engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')

# Save the DataFrame to MySQL
try:
    raw_data.to_sql('transformed_data', con=engine, if_exists='replace', index=False)
    print("Data saved to MySQL database.")
except Exception as e:
    print(f"Error saving data to MySQL: {e}")
# Close the engine connection
engine.dispose()
# Close the S3 client
s3.close()