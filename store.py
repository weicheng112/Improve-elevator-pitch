import pymysql
import json
import os

def lambda_handler(event, context):
    db_host = os.environ['DB_HOST']
    db_user = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWORD']
    db_name = os.environ['DB_NAME']
    
    user_id = event['user_id']
    video_url = event['video_url']
    image_url = event['image_url']
    transcript_url = event['transcript_url']
    feedback = json.dumps(event['feedback'])

    try:
        connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO results (user_id, video_url, image_url, transcript_url, feedback)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, video_url, image_url, transcript_url, feedback))
            connection.commit()

        return {'statusCode': 200, 'body': 'Results stored successfully'}
    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
