#!/usr/bin/env python
# coding: utf-8

# In[1]:


import boto3
import time
from IPython import get_ipython
ipython = get_ipython()

prefix = "hachi-"
upload_bucket_name = prefix + "4452-f21-bao-upload"
end_bucket_name = prefix + "4452-f21-bao-results"

upload_bucket_arn = "arn:aws:s3:::"+upload_bucket_name
end_bucket_arn = "arn:aws:s3:::"+end_bucket_name

lambda_1_name = "upload_handler"
lambda_2_name = "moving_avg_handler"


# In[27]:


get_ipython().run_cell_magic('bash', '', 'cd ~/lambda\npwd\nzip my-deployment-package upload_handler.py\nzip my-deployment-package2 moving_avg_handler.py')


# In[2]:


s3 = boto3.resource('s3')
upload_bucket = s3.Bucket(upload_bucket_name)
resp = upload_bucket.create()
upload_bucket_id = resp['ResponseMetadata']['HostId']
print(upload_bucket_id)


# In[3]:


end_bucket = s3.Bucket(end_bucket_name)
resp = end_bucket.create()
end_bucket_id = resp['ResponseMetadata']['HostId']
print(end_bucket_id)


# In[4]:


iam_client = boto3.client('iam')
role = iam_client.get_role(
    RoleName='robomaker_students'
)
robo_role = role['Role']['Arn']
print(robo_role)


# In[5]:


sns_client = boto3.client('sns')
resp = sns_client.create_topic(
    Name=prefix + 'SYNC',
)
print(resp)


# In[6]:


response = sns_client.list_topics()
arn = response['Topics'][0]['TopicArn']
print(arn)


# In[7]:


topic_arn = resp['TopicArn']
print(topic_arn)


# In[8]:


lambda_client = boto3.client('lambda')
resp = lambda_client.create_function(
    FunctionName=lambda_1_name,
    Handler=lambda_1_name + '.lambda_handler',
    Runtime='python3.7',
    Role=robo_role,
    Code={
        'ZipFile': open('/home/bao/lambda/my-deployment-package.zip', 'rb').read()
    },
    Timeout=600
)
lambda_arn1 = resp['FunctionArn']
print(lambda_arn1)


# In[9]:


resp = lambda_client.create_function(
    FunctionName=lambda_2_name,
    Handler=lambda_2_name + '.lambda_handler',
    Runtime='python3.7',
    Role=robo_role,
    Code={
        'ZipFile': open('/home/bao/lambda/my-deployment-package2.zip', 'rb').read()
    },
    Timeout=600
)
lambda_arn2 = resp['FunctionArn']
print(lambda_arn2)


# In[10]:


resp = lambda_client.add_permission(
    FunctionName=lambda_1_name,
    StatementId='1',
    Action='lambda:InvokeFunction',
    Principal='s3.amazonaws.com',
    SourceArn=upload_bucket_arn
)
print(resp)


# In[11]:

time.sleep(10)
s3_client = boto3.client('s3')
resp = s3_client.put_bucket_notification_configuration(
    Bucket=upload_bucket_name,
    NotificationConfiguration={
        'LambdaFunctionConfigurations': [
            {
                'LambdaFunctionArn': lambda_arn1,
                'Events': [
                    's3:ObjectCreated:Put'
                ]
            }
        ]
    }
)
print(resp)


# In[12]:


resp = lambda_client.add_permission(
    FunctionName=lambda_2_name,
    StatementId='2',
    Action='lambda:InvokeFunction',
    Principal='sns.amazonaws.com',
    SourceArn=topic_arn
)
print(resp)


# In[13]:


resp = sns_client.subscribe(
    TopicArn=topic_arn,
    Protocol='lambda',
    Endpoint=lambda_arn2
)
print(resp)


# In[14]:


response = lambda_client.put_function_event_invoke_config(
    FunctionName=lambda_1_name,
    MaximumRetryAttempts=0,
    MaximumEventAgeInSeconds=3600,
)


# In[15]:


response = lambda_client.put_function_event_invoke_config(
    FunctionName=lambda_2_name,
    MaximumRetryAttempts=0,
    MaximumEventAgeInSeconds=3600,
)
print(response)


# In[ ]:



