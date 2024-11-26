import requests
import json
import os

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    groq_ai_endpoint = os.environ['GROQ_AI_ENDPOINT']
    user_id = event['user_id']
    video_url = event['video_url']
    image_url = event['image_url']
    transcript_url = event['transcript_url']

    try:
        # Send image and subtitle to Groq AI
        response = requests.post(groq_ai_endpoint, json={
            'image_url': image_url,
            'subtitle_url': transcript_url
        })
        feedback = response.json()

        # Trigger database storage Lambda
        lambda_client.invoke(
            FunctionName='StoreResultsFunction',
            InvocationType='Event',
            Payload=json.dumps({
                'user_id': user_id,
                'video_url': video_url,
                'image_url': image_url,
                'transcript_url': transcript_url,
                'feedback': feedback
            })
        )
    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
