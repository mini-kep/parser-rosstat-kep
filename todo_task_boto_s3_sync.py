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
        
        
class RawData:

    def init(year, month):
        self.date = year, month
        # NOT NOW: may check if date is valid 
        
        #S3 bucket:
        #'mini-kep-raw-data'
        
        
    def download_from_s3(self):
        # TODO 1: *download_raw_data_from_s3* download data/raw from s3
        pass    
              
        # listing all objects in S3 bucket https://goo.gl/p4SCv4

    def upload_to_s3(self):
        # TODO 2: *upload_raw_data_to_s3* data/raw to s3
        pass    


def upload_html_docsto_s3():
    pass
    # TODO 3: *doc_upload* upload docs to from s3 mini-kep-docs
    # upload all files from doc\_build\html\ 
    # to aws https://mini-kep-docs.s3.amazonaws.com/
    # mini-kep-docs + is region neded?
        

# for reference:     
# Download Data from S3
# sync_data_from_s3:
# ifeq (default,$(PROFILE))
#	aws s3 sync s3://$(BUCKET)/data/ data/
# else
#	aws s3 sync s3://$(BUCKET)/data/ data/ --profile $(PROFILE)
# endif