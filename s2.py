import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")

# Initialize the S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION_NAME,
)

def upload_to_s3(file_path, s3_folder="uploads/"):
    """
    Uploads a file to an S3 bucket.

    :param file_path: Local file path to upload
    :param s3_folder: Folder in S3 where the file will be stored
    :return: Public URL of the uploaded file
    """
    if not os.path.isfile(file_path):
        print("File does not exist!")
        return None

    file_name = os.path.basename(file_path)
    s3_key = f"{s3_folder}{file_name}"  # Path in S3

    try:
        # Upload file WITHOUT ACL
        s3_client.upload_file(file_path, AWS_STORAGE_BUCKET_NAME, s3_key)

        # Generate file URL
        s3_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
        print(f"File uploaded successfully: {s3_url}")
        return s3_url
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

if __name__ == "__main__":
    file_path = input("Enter the path of the image file to upload: ")
    uploaded_url = upload_to_s3(file_path)
    if uploaded_url:
        print("Uploaded file URL:", uploaded_url)
