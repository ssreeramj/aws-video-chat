import ast
import json
import logging
import os
import urllib.parse

import boto3
import requests
from botocore.exceptions import ClientError

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3_client = boto3.client("s3")


def _generate_presigned_url(bucket_name, file_name, expiration=3600):
    """
    Generates a presigned URL for S3 PUT operation.
    :param bucket_name: S3 bucket name
    :param file_name: File name to be uploaded
    :param expiration: Time in seconds for the presigned URL to remain valid
    """
    try:
        # URL encode the file name to handle special characters
        encoded_file_name = urllib.parse.quote(file_name)

        # Generate the presigned URL for PUT operation
        url = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket_name, "Key": encoded_file_name},
            ExpiresIn=expiration,
            HttpMethod="PUT",
        )
        return url
    except ClientError as e:
        logger.error(f"Error generating presigned URL: {e}")
        return None


def _response(status_code, body):
    """Helper function to create a properly formatted response"""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # Enable CORS for all origins
        },
        "body": json.dumps(body),
    }


def handler(event, context):
    """
    Lambda handler to generate a presigned URL for uploading a file to S3.
    Expects `file_name` and optionally `content_type` as query parameters in the event.
    """
    try:
        if type(event["body"]) == dict:
            event_body = event["body"]
        else:
            event_body = ast.literal_eval(event["body"])
        # Get bucket name from environment variables
        bucket_name = os.environ['BUCKET_NAME']
        file_name = event_body["file_name"]

        # Generate the presigned URL
        url = _generate_presigned_url(bucket_name, file_name)

        if not url:
            logger.error("Failed to generate presigned URL")
            return _response(500, "Could not generate presigned URL")

        logger.info(f"Presigned URL generated for file: {file_name}")

        # Return the presigned URL
        return _response(200, {"presigned_url": url})

    except Exception as e:
        logger.exception(f"Error generating presigned URL: {str(e)}")
        return _response(500, "Internal server error")


if __name__ == "__main__":
    payload = {"body": {"file_name": "sample_code"}}

    response = handler(event=payload, context=None)

    # Test uploading a file using the presigned URL

    def test_upload_with_presigned_url(presigned_url, file_path):
        try:
            with open(file_path, "rb") as file:
                files = {"file": file}
                response = requests.put(presigned_url, data=files)

                if response.status_code == 200:
                    print(
                        f"File uploaded successfully. Status code: {response.status_code}"
                    )
                else:
                    print(f"Failed to upload file. Status code: {response.status_code}")
                    print(f"Response content: {response.content}")
        except Exception as e:
            print(f"Error uploading file: {str(e)}")

    # Example usage
    if response["statusCode"] == 200:
        presigned_url = json.loads(response["body"])["presigned_url"]
        test_file_path = "/home/ssreeramj/projects/side-projects/interview-video-processor/app.py"  # Replace with actual path
        test_upload_with_presigned_url(presigned_url, test_file_path)
    else:
        print("Failed to get presigned URL. Cannot test upload.")
