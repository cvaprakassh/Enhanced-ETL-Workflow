#upload Glue job to the cloud
# Upload the Glue job script to the cloud

aws s3 cp etl_glue_job.py s3://my-etl-project-bucket-project/glue_job/
#check if the upload was successful
if [ $? -ne 0 ]; then
    echo "Error uploading the Glue job script to the cloud."
    exit 1
fi
echo "Upload complete. The Glue job script is now available in the cloud."


#check jar file  available
if [ ! -f "spark-xml_2.12-0.12.0.jar" ]; then
    echo "Jar file not found. Downloading..."
    wget https://repo1.maven.org/maven2/com/databricks/spark-xml_2.12/0.12.0/spark-xml_2.12-0.12.0.jar
fi
# Check if the download was successful
if [ $? -ne 0 ]; then
    echo "Error downloading the jar file."
    exit 1
fi
# Upload the jar file to the cloud
aws s3 cp spark-xml_2.12-0.12.0.jar s3://my-etl-project-bucket-project/glue_job/
# Check if the upload was successful
if [ $? -ne 0 ]; then
    echo "Error uploading the jar file to the cloud."
    exit 1
fi
echo "Upload complete. The jar file is now available in the cloud."


# Check if the upload was successful
if [ $? -ne 0 ]; then
    echo "Error uploading the Glue job script to the cloud."
    exit 1
fi
echo "Upload complete. The Glue job script is now available in the cloud."

aws glue delete-job --job-name "my-etl-glue-job"
# Check if the Glue job deletion was successful
if [ $? -ne 0 ]; then
    echo "Error deleting the Glue job."
    exit 1
fi
echo "Glue job deleted successfully. All resources have been cleaned up."

# Create a Glue job using the AWS CLI
aws glue create-job \
  --name "my-etl-glue-job" \
  --role "arn:aws:iam::762233740664:role/ETL_glue" \
  --command '{"Name": "glueetl", "ScriptLocation": "s3://my-etl-project-bucket-project/glue_job/etl_glue_job.py", "PythonVersion": "3"}' \
  --default-arguments '{
  "--TempDir": "s3://my-etl-project-bucket-project/temp/", 
  "--job-bookmark-option": "job-bookmark-enable",
  "--Etlflow": "full",
  "--extra-jars": "s3://your-bucket/jars/spark-xml_2.12-0.12.0.jar"
  }' \
  --max-retries 1 \
  --timeout 60 \
  --number-of-workers 2 \
  --worker-type "G.1X" \
  --glue-version "2.0"

# Check if the Glue job creation was successful
if [ $? -ne 0 ]; then
    echo "Error creating the Glue job."
    exit 1
fi
echo "Glue job created successfully. You can now run it from the AWS Glue console."
# Run the Glue job and capture RunId
run_id=$(aws glue start-job-run --job-name "my-etl-glue-job" --query 'JobRunId' --output text)

if [ $? -ne 0 ] || [ -z "$run_id" ]; then
    echo "Error starting the Glue job."
    exit 1
fi
echo "Glue job started successfully. Run ID: $run_id"

aws glue get-job-run \
  --job-name "my-etl-glue-job" \
  --run-id "$run_id" \
  --query 'JobRun.Arguments' --output json


# Wait for the Glue job to complete
while true; do
    state=$(aws glue get-job-run --job-name "my-etl-glue-job" --run-id "$run_id" --query 'JobRun.JobRunState' --output text)
    echo "Current job state: $state"
    if [[ "$state" == "SUCCEEDED" || "$state" == "FAILED" || "$state" == "STOPPED" ]]; then
        break
    fi
    sleep 10
done

if [[ "$state" != "SUCCEEDED" ]]; then
    echo "Glue job did not complete successfully. Final state: $state"
    exit 1
fi
echo "Glue job completed successfully. Final state: $state"


# Clean up the Glue job
aws glue delete-job --job-name "my-etl-glue-job"
# Check if the Glue job deletion was successful
if [ $? -ne 0 ]; then
    echo "Error deleting the Glue job."
    exit 1
fi
echo "Glue job deleted successfully. All resources have been cleaned up."
# Clean up the dataset
aws s3 rm s3://my-etl-project-bucket-project/raw/ --recursive
# Check if the dataset deletion was successful
if [ $? -ne 0 ]; then
    echo "Error deleting the dataset from the cloud."
    exit 1
fi
echo "Dataset deleted successfully. All resources have been cleaned up."
# Clean up the temporary files
rm -rf dataset
# Check if the temporary files deletion was successful
if [ $? -ne 0 ]; then
    echo "Error deleting the temporary files."
    exit 1
fi
echo "Temporary files deleted successfully. All resources have been cleaned up."
# Clean up the Glue job script
aws s3 rm s3://my-etl-project-bucket-project/glue_job/ --recursive
# Check if the Glue job script deletion was successful
if [ $? -ne 0 ]; then
    echo "Error deleting the Glue job script from the cloud."
    exit 1
fi
echo "Glue job script deleted successfully. All resources have been cleaned up."
# Clean up the Glue job script
aws s3 rm s3://my-etl-project-bucket-project/temp/ --recursive
# Check if the Glue job script deletion was successful
if [ $? -ne 0 ]; then
    echo "Error deleting the Glue job script from the cloud."
    exit 1
fi
echo "Glue job script deleted successfully. All resources have been cleaned up."

# Clean up the jar file
aws s3 rm s3://my-etl-project-bucket-project/glue_job/ --recursive
# Check if the jar file deletion was successful
if [ $? -ne 0 ]; then
    echo "Error deleting the jar file from the cloud."
    exit 1
fi
echo "Jar file deleted successfully. All resources have been cleaned up."