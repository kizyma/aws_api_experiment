import json
import logging
import boto3
import datetime
from utils import dynamo_db_serializer
from utils.pydantic_datamodel import GenericEvent
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
