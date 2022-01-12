import json
import urllib.parse
import boto3
import time

print('Loading function')

s3 = boto3.client(
    's3',
    region_name='us-east-1'
)
s3_resource = boto3.resource('s3')

sns = boto3.client('sns')


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # Grab the topic arn
    response = sns.list_topics()
    topic_arn = response['Topics'][0]['TopicArn']

    try:
        response = s3.get_object(Bucket=bucket, Key=key)

        # Get the file. Parse into string. then split string into list
        obj = s3_resource.Object(bucket, key)
        contents = obj.get()['Body'].read().decode('utf-8')
        content_list = contents.splitlines()

        print("CONTENT TYPE: " + response['ContentType'])

        # Send all lines to SNS other than first and last
        for line in content_list[1:-1]:
            print("Sending: " + line)
            sns.publish(
                TopicArn=topic_arn,
                Message=line
            )
            time.sleep(10)

        # Last entry. Strip the ends. Send out special note.
        line = content_list[-1]
        line = line[1:-1]

        special_note = "!" + line
        print("Sending: " + special_note)
        sns.publish(
            TopicArn=topic_arn,
            Message=special_note
        )
        return response['ContentType']
    except Exception as e:
        print(e)
        print(
            'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                key, bucket))
        raise e
