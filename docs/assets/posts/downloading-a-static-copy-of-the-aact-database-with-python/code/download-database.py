import requests
import zipfile
from pathlib import Path
from urllib.parse import urljoin


# Get current working directory
ROOT_DIR = Path().cwd()

# Create the downloads directory
DOWNLOADS_DIR = ROOT_DIR.joinpath("downloads")
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Create the directory where data will be stored
DATA_DIR = ROOT_DIR.joinpath("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Select the desired date of the database
DATE_OF_DATABASE = "2024-03-01"

# Assign a name to the directory where the raw data will be stored
DB_DIR_NAME = f"{DATE_OF_DATABASE}_aact_database"

# Assign a name to the downloaded zip file
DOWNLOAD_DB_FILE_NAME = f"{DB_DIR_NAME}.zip"

# Create the complete download path for the zipfile
DOWNLOAD_PATH = DOWNLOADS_DIR.joinpath(DOWNLOAD_DB_FILE_NAME)

# Create the complete path where the database will be unzipped
UNZIP_DESTINATION_PATH = DATA_DIR.joinpath(DB_DIR_NAME)

# Build the URL
URL = urljoin("https://aact.ctti-clinicaltrials.org/static/static_db_copies/daily/", DATE_OF_DATABASE)

# Download the file
response = requests.get(URL, stream=True)

# Get the total file size in bytes
total_size = int(response.headers.get('content-length', 0))

# Print the total file size in MB
print(f"Total size: {total_size/1024/1024:.2f} MB")

# Open a file for writing in binary mode
with open(DOWNLOAD_PATH, 'wb') as f:
    # Iterate over the response content with a chunk size of 1024 bytes
    print(f"Starting download: {DOWNLOAD_PATH}")
    for data in response.iter_content(chunk_size=1024):
        # Write each chunk to the file
        f.write(data)
    print(f"Finished download: {DOWNLOAD_PATH}")

# Unzip the file
with zipfile.ZipFile(DOWNLOAD_PATH, "r") as zip_file:
    zip_file.extractall(UNZIP_DESTINATION_PATH)

# Print the path where the database was unzipped
print(f"Database downloaded and unzipped at {UNZIP_DESTINATION_PATH}")
