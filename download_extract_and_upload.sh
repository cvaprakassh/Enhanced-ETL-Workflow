#!/bin/bash

# This script downloads and extracts the Dataset

echo "Downloading Dataset..."
wget -q --show-progress --progress=bar:force:noscroll -O dataset.zip https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0221EN-SkillsNetwork/labs/module%206/Lab%20-%20Extract%20Transform%20Load/data/source.zip
if [ $? -ne 0 ]; then
    echo "Error downloading the dataset."
    exit 1
fi
echo "Download complete. Extracting files..."
unzip -q dataset.zip -d dataset
if [ $? -ne 0 ]; then
    echo "Error extracting the dataset."
    exit 1
fi
echo "Extraction complete. Cleaning up..."
rm dataset.zip
if [ $? -ne 0 ]; then
    echo "Error cleaning up."
    exit 1
fi
echo "All done! The dataset is ready for use."
echo "You can find the extracted files in the current directory."

echo "uploading dataset to the cloud..."
# Upload the dataset to the cloud
# (Assuming you have a cloud storage CLI tool installed and configured)

aws s3 cp ./dataset s3://my-etl-project-bucket-project/raw/ --recursive

#Check if the upload was successful
if [ $? -ne 0 ]; then
    echo "Error uploading the dataset to the cloud."
    exit 1
fi
echo "Upload complete. The dataset is now available in the cloud."
