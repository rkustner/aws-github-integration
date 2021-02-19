import json
import boto3
import os
import requests
from nacl import encoding,public
from botocore.exceptions import ClientError
from base64 import b64encode
import os

def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def get_pub_key(owner_repo, github_token):
    # get public key for encrypting
    pub_key_ret = requests.get(
        f'https://api.github.com/repos/{owner_repo}/actions/secrets/public-key',
        headers={'Authorization': f"token {github_token}"}
    )

    if not pub_key_ret.status_code == requests.codes.ok:
        raise Exception(f"github public key request failed, status code: {pub_key_ret.status_code}, body: {pub_key_ret.text}, vars: {owner_repo} {github_token}")
        sys.exit(1)

    #convert to json
    public_key_info = pub_key_ret.json()

    #extract values
    public_key = public_key_info['key']
    public_key_id = public_key_info['key_id']

    return (public_key, public_key_id)

def upload_secret(owner_repo,key_name,encrypted_value,pub_key_id,github_token):
    #upload encrypted access key
    updated_secret = requests.put(
        f'https://api.github.com/repos/{owner_repo}/actions/secrets/{key_name}',
        json={
            'encrypted_value': encrypted_value,
            'key_id': pub_key_id
        },
        headers={'Authorization': f"token {github_token}"}
    )
    # status codes github says are valid
    good_status_codes = [204,201]

    if updated_secret.status_code not in good_status_codes:
        print(f'Got status code: {updated_secret.status_code} on updating {key_name} in {owner_repo}')
        sys.exit(1)
    print(f'Updated {key_name} in {owner_repo}')

USER_ARN = "arn:aws:iam::690167127138:user/ProvisionGithubSecretsStack-GithubUser36C2AAC7-1RF46UCFLWB2N"
github_token = 'undefined'
repo = 'rkustner/hello-github-actions'
access_key_name = "access_key_id"
secret_key_name = "secret_key_id"

iam = boto3.client('iam')

# Get githubtoken from Secrets Manager
session = boto3.session.Session()
sm = session.client(service_name='secretsmanager', region_name='eu-west-1')

try:
    get_secret_value_response = sm.get_secret_value(SecretId='githubtoken')
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceNotFoundException':
        print("The requested secret " + secret_name + " was not found")
    elif e.response['Error']['Code'] == 'InvalidRequestException':
        print("The request was invalid due to:", e)
    elif e.response['Error']['Code'] == 'InvalidParameterException':
        print("The request had invalid params:", e)
else:
    github_token = get_secret_value_response['SecretString']

body = ""
(pre, username) = USER_ARN.split("/")

# List all Access Keys from IAM user
response = iam.list_access_keys(UserName=username)
akeys = response['AccessKeyMetadata']
numkeys = len(akeys)

# Loop through all accesskeys and print them
for k in akeys:
    print(k['AccessKeyId'])

# If we don't have an accesskey, create one and store it in github secrets
if numkeys == 0:
    # create access key
    newkey_response = iam.create_access_key(UserName=username)
    accesskey = newkey_response['AccessKey']
    accesskey_id = accesskey['AccessKeyId']
    accesskey_secret = accesskey['SecretAccessKey']

    # store secret in github secrets
    (public_key, pub_key_id) = get_pub_key(repo, github_token)
    encrypted_access_key = encrypt(public_key, accesskey_id)
    encrypted_secret_key = encrypt(public_key, accesskey_secret)   
    upload_secret(repo, access_key_name, encrypted_access_key, pub_key_id, github_token)
    upload_secret(repo, secret_key_name, encrypted_secret_key, pub_key_id, github_token)

body = "User ARN = %s\nNumber of keys is %d" % (USER_ARN, numkeys)

print(body)
