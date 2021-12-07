import json
import logging
import boto3
import datetime

from boto3.dynamodb.conditions import Key, Attr
from utils import dynamo_db_serializer
from utils.pydantic_datamodel import GenericEvent, convert_datetime_to_iso_8601_with_z_suffix
from pydantic import ValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.client('dynamodb')
table_name = 'events'


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
                         "start_date": str(event.start_date), "end_date": str(event.end_date)}
    except ValidationError:
        response = {
            "statusCode": 400,
            "body": "Bad Request. Data validation has been failed."
                    "Please check input data types & make sure they correspond to the requirements."
        }

    res = dynamodb.put_item(
        TableName=table_name, Item=dynamo_db_serializer.to_item(event_to_dict))

    # If creation is successful
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        response = {
            "statusCode": 201,
        }

    return response


def get_all(event, context):
    # Set the default error response
    response = {
        "statusCode": 500,
        "body": "An error occured while getting all posts."
    }
    now_str = convert_datetime_to_iso_8601_with_z_suffix(datetime.utcnow())
    day_ago_str = convert_datetime_to_iso_8601_with_z_suffix(datetime.utcnow() - datetime.timedelta(hours=24))

    fe = Key('end_date').between(day_ago_str, now_str);
    scan_result = dynamodb.scan(TableName=table_name, FilterExpression=fe)
    posts = []

    for item in scan_result:
        posts.append(dynamo_db_serializer.to_dict(item))

    response = {
        "statusCode": 200,
        "body": json.dumps(posts)
    }

    return response
