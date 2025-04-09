# AWS ETL Pipeline: CSV, JSON, and XML Data Processing

This project demonstrates an **ETL (Extract, Transform, Load)** pipeline using Python, AWS services (S3, RDS, Glue), and multiple data formats (CSV, JSON, XML).

---

## 📁 Step 1: Gather Data Files

1. **Download the Dataset**

Open a terminal and run:

```bash
wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0221EN-SkillsNetwork/labs/module%206/Lab%20-%20Extract%20Transform%20Load/data/source.zip
```

2. **Unzip the Dataset**

Use one of the following commands:

**Linux/macOS:**
```bash
unzip source.zip -d ./unzipped_folder
```

**Windows PowerShell:**
```powershell
Expand-Archive -Path source.zip -DestinationPath ./unzipped_folder
```

> ✅ After this step, your folder will contain `.csv`, `.json`, and `.xml` files for processing.

---

## ☁️ Step 2: AWS Setup

### 1. Create an S3 Bucket

This bucket stores:
- Raw data files (CSV, JSON, XML)
- Transformed CSV output

📌 **Example bucket name:** `my-etl-project-bucket`

### 2. Set Up AWS RDS

- Create a MySQL/PostgreSQL instance.
- Configure **security groups** to allow access from your IP or Lambda.

### 3. (Optional) Set Up AWS Glue

- Create a **Glue Crawler** to detect the raw file schemas.
- Use **Glue Jobs** for automated ETL tasks and scheduling.

---

## 🧰 Step 3: Import Libraries and Configure AWS

### Required Python Libraries

```bash
pip install boto3 pandas sqlalchemy pymysql
```

### Libraries Used
- `boto3` – AWS SDK for S3 and Glue
- `pandas` – Data manipulation
- `sqlalchemy` – Connect and insert data into RDS

Make sure your AWS credentials are configured:
- Via environment variables
- Or `~/.aws/credentials` file

---

## 🛠️ Step 4: Define ETL Pipeline

### 🔍 Extract
- Upload raw `.csv`, `.json`, and `.xml` files to your S3 bucket.
- Download them back into the script for transformation.

### 🔄 Transform
- Standardize column names.
- Convert:
  - **Inches ➡️ Meters**
  - **Pounds ➡️ Kilograms**
- Remove duplicates and handle missing values.

### 🚀 Load

#### 1. Upload to S3
- Save the final transformed file back to S3 as `transformed_data.csv`.

#### 2. Upload to RDS
- Use SQLAlchemy to insert the DataFrame into a relational database table.

#### (Optional) Use AWS Glue
- Automate ETL using Glue by reading from raw S3 paths and writing to RDS or another S3 location.

---

## 📜 Step 5: Logging

- Use Python’s `logging` module to track ETL progress.
- Save logs to a local file (e.g., `/tmp/etl_log_timestamp.log`).
- Upload the log file to S3 for centralized access.

```python
logging.basicConfig(
    filename='/tmp/etl_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## ▶️ Step 6: Execution Order

1. **Upload Raw Files to S3**
   - Extract files from ZIP
   - Upload to your S3 bucket

2. **Extract & Transform**
   - Read from S3
   - Perform transformations locally

3. **Load Transformed Data**
   - Save to S3 as `transformed_data.csv`
   - Insert into RDS using SQLAlchemy

4. **Monitor Logs**
   - Ensure logs are saved locally or in S3 for review

---

## 🧪 Testing & Verification

- Query your RDS instance using MySQL Workbench or pgAdmin.
- Check transformed CSV in S3.
- Review logs to ensure successful execution.

---

## ✅ Prerequisites

- AWS Account with access to S3, RDS, and Glue
- IAM Role or User with proper permissions
- Python 3.7+
- Internet access to download dataset

---

## 📬 Contact

For issues or questions, feel free to reach out via GitHub Issues or email.
