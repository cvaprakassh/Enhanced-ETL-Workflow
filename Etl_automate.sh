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
make setup     # Sets up virtualenv and installs packages
make run       # Runs your ETL script
make clean     # Deletes the virtualenv
echo "📈 Data transformation is complete and updated RDS cloud..."

echo "✅ All scripts completed successfully!"
echo "🚀 ETL process completed!"

echo "🗑️ Cleaning up temporary files..."
# Clean up the temporary files
rm -rf dataset
# Check if the temporary files deletion was successful
if [ $? -ne 0 ]; then
    echo "Error deleting the temporary files."
    exit 1
fi      
echo "🗑️ Temporary files deleted successfully. All resources have been cleaned up."

#clean dataset
aws s3 rm s3://my-etl-project-bucket-project/raw/ --recursive
# Check if the dataset deletion was successful
if [ $? -ne 0 ]; then
    echo "Error deleting the dataset from the cloud."
    exit 1
fi
echo "🗑️ Dataset deleted successfully. All resources have been cleaned up."

