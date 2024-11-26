import boto3
import subprocess
import os
import json

s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    bucket_name = os.environ['VIDEO_BUCKET_NAME']
    output_bucket = os.environ['IMAGES_BUCKET_NAME']
    file_name = event['file_name']
    video_url = event['video_url']
    user_id = event['user_id']
    
    video_path = f"/tmp/{file_name}"
    image_path = f"/tmp/{file_name.split('.')[0]}_middle_frame.jpg"

    try:
        # Download video from S3
        s3.download_file(bucket_name, file_name, video_path)

        # Get video duration and extract middle frame
        result = subprocess.run(
            f"ffprobe -i {video_path} -show_entries format=duration -v quiet -of csv=p=0",
            shell=True,
            capture_output=True,
            text=True
        )
        duration = float(result.stdout.strip())
        middle_time = duration / 2

        subprocess.run(
            f"ffmpeg -i {video_path} -vf \"select='eq(n\,0)'\" -frames:v 1 -ss {middle_time} {image_path}",
            shell=True
        )

        # Upload middle frame to S3
        image_s3_key = f"frames/{file_name.split('.')[0]}_middle_frame.jpg"
        s3.upload_file(image_path, output_bucket, image_s3_key)
        image_url = f"https://{output_bucket}.s3.amazonaws.com/{image_s3_key}"

        # Trigger subtitle extraction Lambda
        lambda_client.invoke(
            FunctionName='ExtractSubtitlesFunction',
            InvocationType='Event',
            Payload=json.dumps({
                'user_id': user_id,
                'file_name': file_name,
                'video_url': video_url,
                'image_url': image_url
            })
        )

    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
