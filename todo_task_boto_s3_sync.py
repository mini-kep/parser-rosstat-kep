import boto3
import botocore

# Setup AWS credentials as in 
# https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration
#
#  cd %HOMEDRIVE%\%HOMEPATH%
#  md .aws
#  cd .aws
#  touch credentials
#  [default]
#   aws_access_key_id = ...
#   aws_secret_access_key = ...
#

BUCKET_NAME = 'mini-kep-docs' # replace with your bucket name
KEY = 'index.html' # replace with your object key

s3 = boto3.resource('s3')


for bucket in s3.buckets.all():
    print(bucket.name)

# https://boto3.readthedocs.io/en/latest/guide/s3-example-download-file.html

try:
    s3.Bucket(BUCKET_NAME).download_file(KEY, 'index.html')
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
        print("The object does not exist.")
    else:
        raise
        
# TODO 1: *get_s3_data* download data/raw from s3
    
# Download Data from S3
# sync_data_from_s3:
# ifeq (default,$(PROFILE))
#	aws s3 sync s3://$(BUCKET)/data/ data/
# else
#	aws s3 sync s3://$(BUCKET)/data/ data/ --profile $(PROFILE)
# endif
        
# TODO 2: *doc_upload* upload docs to from s3 mini-kep-docs
#         from doc\_build\html       