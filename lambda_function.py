import boto3
import pymysql
import json
import os
import logging
from botocore.exceptions import NoCredentialsError, ClientError

# Initialize clients and logger
s3 = boto3.client('s3','us-east-1')
polly = boto3.client('polly')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
BUCKET_NAME = os.environ['BUCKET_NAME']


def async_upload_to_s3(bucket_name, file_name, file_content):
    """
    Upload a file asynchronously to S3.
    """
    logger.info("Starting asynchronous upload to S3: %s", file_name)
    try:
        response = s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=file_content
        )
        logger.info("Asynchronous upload to S3 completed: %s", response)
        return f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
    except ClientError as e:
        logger.error("Error during S3 upload: %s", str(e))
        raise

def extract_audio_text(video_url):
    """
    Placeholder function to handle audio transcription.
    Replace this function with the actual logic to extract text from video/audio.
    """
    logger.info(f"Extracting audio text from: {video_url}")
    # TODO: Integrate with AWS Transcribe or another service
    return "This is a placeholder subtitle text extracted from the video."

def lambda_handler(event, context):
    try:
        # Extract file details from the event
        logger.info("Received event: %s", json.dumps(event))
        file_content = event['body']
        file_name = event['headers']['file-name']
        user_id = event['headers']['user-id']

        # Check if the bucket is accessible
        # if not check_s3_bucket(BUCKET_NAME):
        #     return {
        #         'statusCode': 500,
        #         'body': json.dumps({'error': f"S3 bucket {BUCKET_NAME} is not accessible."})
        #     }

        # 1. Upload video to S3 asynchronously
        video_url = async_upload_to_s3(BUCKET_NAME, file_name, file_content)
        logger.info("Video successfully uploaded to S3: %s", video_url)

        # 2. Insert metadata into RDS
        logger.info("Connecting to RDS: %s", DB_HOST)
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        try:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO user_video (user_id, video_url)
                VALUES (%s, %s)
                """
                cursor.execute(insert_query, (user_id, video_url))
                connection.commit()
                logger.info("Video metadata inserted into RDS for user_id: %s", user_id)
        finally:
            connection.close()

        # 3. Process the video with AWS Polly
        logger.info("Processing video with AWS Polly")
        subtitle_text = extract_audio_text(video_url)
        subtitle_response = polly.synthesize_speech(
            Text=subtitle_text,
            OutputFormat='json',
            VoiceId='Joanna'
        )
        subtitle_file = subtitle_response['AudioStream'].read()
        subtitle_key = f"{file_name.split('.')[0]}_subtitles.json"
        subtitle_url = async_upload_to_s3(BUCKET_NAME, subtitle_key, subtitle_file)
        logger.info("Subtitles uploaded to S3: %s", subtitle_url)

        # 4. Update the RDS record with subtitle URL
        logger.info("Updating RDS with subtitle URL")
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        try:
            with connection.cursor() as cursor:
                update_query = """
                UPDATE user_video
                SET subtitle_url = %s
                WHERE video_url = %s
                """
                cursor.execute(update_query, (subtitle_url, video_url))
                connection.commit()
                logger.info("Subtitle URL updated in RDS for video_url: %s", video_url)
        finally:
            connection.close()

        # Success response
        return {
            'statusCode': 200,
            'body': json.dumps({'video_url': video_url, 'subtitle_url': subtitle_url})
        }

    except NoCredentialsError as e:
        logger.error("Credentials error: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': "AWS credentials error. Please check your IAM permissions."})
        }

    except ClientError as e:
        logger.error("AWS client error: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': "AWS service error. Please check your services and resources."})
        }

    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
