# aws lambda for pastebin handling
# emails received by SES
# pastes stored in S3
# records stored in dynamo

from __future__ import print_function
import base64
import boto3
import json
import re
import uuid
from botocore.vendored import requests

s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
dyntable = dynamodb.Table('paste_links')


def retrieve_paste(url):
    raw_url = "https://pastebin.com/raw{}".format(url[url.rindex('/'):])
    print("paste retrival for {} in progress..".format(raw_url))
    r = requests.get(raw_url, verify=False)
    if r.ok:
        return r.text
    return None

def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    pb_keyword = re.compile("(?<=')[^']+(?=')")
    pb_url = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')    
    
    try:
        ts = message['mail']['timestamp']
        body = base64.b64decode(message['content'])
        kw = pb_keyword.findall(body)[0].replace("/", "")
        u = pb_url.findall(body)[0]
        pc = retrieve_paste(u)
        pid = u[u.rindex('/')+1:]
        
        s3_filepath = "MY-PATH/{kw}-{ts}-{pid}-pastecontent.txt".format(
            ts=ts,
            kw=kw,
            pid=pid,
        )
        s3.Bucket('MY-BUCKET').put_object(Key=s3_filepath, Body=pc)
        print("paste written to: {}".format(s3_filepath))
        

        response = dyntable.put_item(
           Item={
                'ID': str(uuid.uuid4()),
                'keyword': kw,
                'ts': ts,
                'id': pid,
                'client': 'personal',
                'url': u,
                'mail_body': body,
                'paste_content_path': s3_filepath,
            }
        )

        print("Added record to dynamo!")
 
    except Exception as e:
        print("Caught exception: " + str(e))
        return False
        
    
    return message
