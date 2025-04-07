import boto3
import pandas as pd
import io

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
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
