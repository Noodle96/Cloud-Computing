# """An AWS Python Pulumi program"""

# import pulumi
# from pulumi_aws import s3

# # Create an AWS resource (S3 Bucket)
# bucket = s3.Bucket('my-bucket')

# # Export the name of the bucket
# pulumi.export('bucket_name', bucket.id)
# __main__.py
from typing import Any
import pulumi
import pulumi_aws as aws

def create_test_queue() -> aws.sqs.Queue:
    q: aws.sqs.Queue = aws.sqs.Queue(
        "lab-test-queue",
        # visibility_timeout_seconds=30,
    )
    return q

if __name__ == "__main__":
    queue: aws.sqs.Queue = create_test_queue()
    pulumi.export("queue_url", queue.id)
