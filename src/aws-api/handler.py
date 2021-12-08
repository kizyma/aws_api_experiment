import json
import logging
import boto3
import datetime

from boto3.dynamodb.conditions import Key, Attr
from utils import dynamo_db_serializer
from utils.pydantic_datamodel import GenericEvent, utc_timestamp
from pydantic import ValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Default region for both client and resource is region_name="us-east-1"
# Will leave it out for now

table_name = 'events'
# Creating the DynamoDB Client
dynamodb_client = boto3.client('dynamodb')
# Creating the DynamoDB Table Resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)


def create(event, context):
    logger.info(f'Incoming request is: {event}')

    # Set the default error response
    response = {
        "statusCode": 500,
        "body": "An error occurred while creating post."
    }
    post_str = event['body']
    try:
        event = GenericEvent.parse_raw(post_str)
        event_to_dict = {"event_id": event.event_id, "event_name": event.event_name, "status": event.status,
                         "start_date": event.start_date.isoformat(), "end_date": event.end_date.isoformat(),
                         "timestamp": utc_timestamp(event.end_date)}
        res = dynamodb_client.put_item(
            TableName=table_name, Item=dynamo_db_serializer.to_item(event_to_dict))

        # If creation is successful
        if res['ResponseMetadata']['HTTPStatusCode'] == 200:
            response = {
                "statusCode": 201,
            }
    except ValidationError:
        response = {
            "statusCode": 400,
            "body": "Bad Request. Data validation has been failed."
                    "Please check input data types & make sure they correspond to the requirements."
        }

    return response


def get_all(event, context):
    # Set the default error response
    response = {
        "statusCode": 500,
        "body": "An error occurred while getting all posts."
    }
    now_dt = datetime.datetime.utcnow()
    day_ago_dt = now_dt - datetime.timedelta(hours=24)
    response = table.query(
        IndexName='timeEventsIndex',
        KeyConditionExpression=Key('end_date').between(day_ago_dt.isoformat(), now_dt.isoformat())
    )

    # fe = f"end_date BETWEEN :{day_ago_dt.isoformat()} and {now_dt.isoformat()}"
    # scan_result = dynamodb_client.scan(TableName=table_name, FilterExpression=fe)
    posts = []

    for item in response:
        posts.append(dynamo_db_serializer.to_dict(item))

    response = {
        "statusCode": 200,
        "body": json.dumps(posts)
    }

    return response
