import boto3
from botocore.exceptions import ClientError
from flask import current_app
import logging

def get_s3_client():
    """Get configured S3 client"""
    return boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_REGION']
    )

def upload_file_to_s3(file_obj, filename):
    """Upload a file to S3"""
    s3_client = get_s3_client()
    bucket_name = current_app.config['AWS_BUCKET_NAME']
    
    # Determine content type based on file extension
    content_type = 'application/octet-stream'  # default binary
    if filename.lower().endswith('.pdf'):
        content_type = 'application/pdf'
    elif filename.lower().endswith('.txt'):
        content_type = 'text/plain'
    elif filename.lower().endswith('.docx'):
        content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    try:
        extra_args = {
            'ContentType': content_type,
            'ACL': 'private'
        }
        
        # If file_obj has content_type, use that instead
        if hasattr(file_obj, 'content_type'):
            extra_args['ContentType'] = file_obj.content_type
        
        s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            filename,
            ExtraArgs=extra_args
        )
        return f"s3://{bucket_name}/{filename}"
    except ClientError as e:
        logging.error(f"Error uploading file to S3: {e}")
        raise

def delete_file_from_s3(file_path):
    """Delete a file from S3"""
    s3_client = get_s3_client()
    bucket_name = current_app.config['AWS_BUCKET_NAME']
    
    # Extract key from s3://bucket/key format
    key = file_path.replace(f"s3://{bucket_name}/", "")
    
    try:
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=key
        )
    except ClientError as e:
        logging.error(f"Error deleting file from S3: {e}")
        raise

def get_file_from_s3(file_path):
    """Get a file from S3"""
    s3_client = get_s3_client()
    bucket_name = current_app.config['AWS_BUCKET_NAME']
    
    # Extract key from s3://bucket/key format
    key = file_path.replace(f"s3://{bucket_name}/", "")
    
    try:
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=key
        )
        return response['Body']
    except ClientError as e:
        logging.error(f"Error getting file from S3: {e}")
        raise

def generate_presigned_url(file_path, expiration=3600):
    """Generate a presigned URL for a file in S3"""
    s3_client = get_s3_client()
    bucket_name = current_app.config['AWS_BUCKET_NAME']

    # Extract key from s3://bucket/key format
    key = file_path.replace(f"s3://{bucket_name}/", "")

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        logging.error(f"Error generating presigned URL: {e}")
        raise