import boto3
from datetime import datetime
import random
import re
from botocore.exceptions import ClientError

## === setup items === ##
BUCKET_NAME = "trellisense-raw-sudoe"

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
## === === ##

#arbitrary start and end dates
start_date = datetime(2024, 6, 1)
end_date = datetime(2025, 6, 1)

date_array = [''] * 10
file_norm = [''] * 10
file_p1 = [''] * 10
file_p2 = [''] * 10

# random file generation, uncomment if new files need to be created

# for i in range(10):
#     rand_date = start_date + (end_date - start_date) * random.random()
#     formatted = rand_date.strftime("%Y%m%d_%H%M%S")
#     date_array[i] = formatted
#     file_norm[i] = 'AVG_' + date_array[i] + '.txt'
#     file_p1[i] = 'AVG_Path-1_' + date_array[i] + '.txt'
#     file_p2[i] = 'AVG_Path-2_' + date_array[i] + '.txt'

#     response = s3_client.put_object(
#     Bucket=BUCKET_NAME,
#     Key = 's9000/'+ file_norm[i],
#     Body = 'hi hello hi'
# )
# s3_key = []
# date_str = []

## === core code === ##
bucket = s3.Bucket(BUCKET_NAME)

def exists(key):
    try:
        s3.Object(BUCKET_NAME, key).load()
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise

for i, file in enumerate(bucket.objects.filter(Prefix='s9000/')):
    
    if re.search(r'^s\d+/', file.key):
        file_rem = re.sub(r'^s\d+/', '', file.key)

        if re.match(r'AVG_Path-1_', file_rem):
            avg_rem = re.sub(r'AVG_Path-1_', '', file_rem)
        elif re.match(r'AVG_Path-2_', file_rem):
            avg_rem = re.sub(r'AVG_Path-2_', '', file_rem)
        elif re.match(r'AVG_', file_rem):
            avg_rem = re.sub(r'AVG_', '', file_rem)
        else:
            continue

        # remove file extension
        date = re.sub(r'\.txt$', '', avg_rem)

        # parse datetime
        dt = datetime.strptime(date, "%Y%m%d_%H%M%S")

        year  = dt.strftime("%Y")
        month = dt.strftime("%m")
        day   = dt.strftime("%d")

        folder_year = f"s9000/{year}/"
        folder_month = f"s9000/{year}/{month}/"
        folder_day = f"s9000/{year}/{month}/{day}/"

        # create folders if they don't exist
        if not exists(folder_year):
            s3_client.put_object(Bucket=BUCKET_NAME, Key=folder_year)

        if not exists(folder_month):
            s3_client.put_object(Bucket=BUCKET_NAME, Key=folder_month)

        if not exists(folder_day):
            s3_client.put_object(Bucket=BUCKET_NAME, Key=folder_day)

        relative_key = file.key[len("s9000/"):]

        new_key = f"{folder_day}{relative_key}"

        s3.Object(BUCKET_NAME, new_key).copy_from(
            CopySource={'Bucket': BUCKET_NAME, 'Key': file.key}
        )

        s3.Object(BUCKET_NAME, file.key).delete()
## === === ##