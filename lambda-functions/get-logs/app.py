import requests
import gzip
import base64
import json
import os

''' Resources
https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/SubscriptionFilters.html#LambdaFunctionExample
https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html
'''
SLACK_INCOMING_WEBHOOK = os.getenv("SLACK_INCOMING_WEBHOOK")

def handler(event, context):
    # Step 1: Get Base64 and gzip formatted data
    data_base64 = event['awslogs']['data']
    data_base64_bytes = bytes(data_base64, "utf-8")
    
    # Step 2: Decode base64
    data_gzip = base64.b64decode(data_base64_bytes)

    # Step 3: Gunzip formatted data
    data = gzip.decompress(data_gzip).decode()
    data_json = json.loads(data)
    print(data_json)
    print(data_json['logEvents'])
    
    # Step 4: Loop log list and post to Slack
    for log in data_json['logEvents']:
        message = "{} — {} — {}".format(
            data_json['logGroup'], log['timestamp'], log['message'])
        headers = {"Content-type": "application/json"}
        payload = {"text": message}
        print(payload)
        r = requests.post(SLACK_INCOMING_WEBHOOK,
                          headers=headers, json=payload)
        print(r.status_code)
        print(r.text)
