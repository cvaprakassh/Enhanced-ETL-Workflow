#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting ETL process..."
echo "📥 Downloading and extracting dataset..."

# Download and extract the dataset
bash download_extract_and_upload.sh
echo "📤 Dataset uploaded to the cloud..."

echo "📊 Transforming data..."
# Transform the data
python3 read_and_transform.py
echo "📈 Data transformation is complete and updated RDS cloud..."

echo "✅ All scripts completed successfully!"
exho "🚀 ETL process completed!"