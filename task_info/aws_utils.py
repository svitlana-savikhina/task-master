import boto3


def create_aws_client(service_name: str):
    client = boto3.client(
        service_name, endpoint_url="http://localstack:4566", region_name="eu-central-1"
    )
    return client
