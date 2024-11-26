import boto3
import time
import json

transcribe = boto3.client('transcribe')
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    video_url = event['video_url']
    file_name = event['file_name']
    user_id = event['user_id']
    image_url = event['image_url']
    job_name = f"TranscriptionJob-{file_name.replace('.', '-')}"
    
    try:
        # Start transcription job
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': video_url},
            MediaFormat='mp4',
            LanguageCode='en-US'
        )

        # Poll for transcription job completion
        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            time.sleep(5)

        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            transcript_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
            # Trigger Groq AI analysis Lambda
            lambda_client.invoke(
                FunctionName='AnalyzeWithGroqFunction',
                InvocationType='Event',
                Payload=json.dumps({
                    'user_id': user_id,
                    'video_url': video_url,
                    'image_url': image_url,
                    'transcript_url': transcript_url
                })
            )
        else:
            raise Exception("Transcription job failed")

    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
