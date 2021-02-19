import json
import boto3
import os

USER_ARN = os.environ['userArn']

iam = boto3.client('iam')

def handler(event, context):

    body = ""

    # arn:aws:iam::690167127138:user/ProvisionGithubSecretsStack-GithubUser36C2AAC7-1RF46UCFLWB2N
    (pre, username) = USER_ARN.split("/")
    response = iam.list_access_keys(UserName=username)
    akeys = response['AccessKeyMetadata']
    numkeys = len(akeys)

    accesskey_list = ""

    for k in akeys:
        accesskey_id = k['AccessKeyId']
        accesskey_list = accesskey_list + accesskey_id + " "

    # only generate IAM Access Key if we have 0 keys 
    if numkeys == 0:
        newkey_response = iam.create_access_key(UserName=username)
        accesskey = newkey_response['AccessKey']
        accesskey_id = accesskey['AccessKeyId']

    body = "User ARN = %s -- Number of keys is %d -- List of keys: %s" % (USER_ARN, numkeys, accesskey_list)

    return {
        "statusCode": 200,
        "headers": { "Content-type": "text/html"} ,
        "body": body
    }