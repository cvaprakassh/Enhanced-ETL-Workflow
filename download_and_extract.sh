#!/bin/bash

# This script downloads and extracts the Dataset

echo "Downloading Dataset..."
wget -q --show-progress --progress=bar:force:noscroll -O dataset.zip https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0221EN-SkillsNetwork/labs/module%206/Lab%20-%20Extract%20Transform%20Load/data/source.zip
if [ $? -ne 0 ]; then
    echo "Error downloading the dataset."
    exit 1
fi
echo "Download complete. Extracting files..."
unzip -q dataset.zip
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
