import logging
import boto3
import datetime
import simplejson as json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from utils import dynamo_db_serializer
from utils.pydantic_datamodel import GenericEvent
from utils.time_serializer import utc_timestamp
from pydantic import ValidationError
from itertools import chain

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
    """
    Function to create event from user input. In case some optional fields are missing - fill them out via pydantic.
    For more info on data model, validation and data serialization, please consult pydantic_datamodel module.
    :param event:
    :param context:
    :return: response, notifies user about the result of the operation
    """
    logger.info(f'Incoming request is: {event}')
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


def _get_events_by_status(status) -> list:
    """
    Service method to retrieve events from the last 24 hrs by their status
    :param status: str parameter
    :return: list of retrieved events, already properly formatted
    """
    now_dt = datetime.datetime.utcnow()
    now_timestamp = utc_timestamp(now_dt)
    day_ago_dt = now_dt - datetime.timedelta(hours=24)
    day_ago_timestamp = utc_timestamp(day_ago_dt)
    response = table.query(
        IndexName='statusTimestampIndex',
        KeyConditionExpression=Key('status').eq(status) & Key('timestamp')
            .between(day_ago_timestamp, now_timestamp)
    )

    events = []
    if response["Items"] is not None:
        for item in response["Items"]:
            output_item = {"end_date": item["end_date"], "start_date": item["start_date"],
                           "status": item["status"], "event_id": item["event_id"],
                           "event_name": item["event_name"]}
            events.append(output_item)
    return events


def get_all(event, context):
    """
    Function to retrieve all events. Make 3 separate calls, to get all known event statuses, then chain lists with events
    via itertools.chain
    :param event:
    :param context:
    :return:
    """
    try:
        completed_events = _get_events_by_status('completed')
        active_events = _get_events_by_status('active')
        inactive_events = _get_events_by_status('inactive')
        all_events = list(chain(completed_events, active_events, inactive_events))

        response = {
            "statusCode": 200,
            "body": json.dumps(all_events)
        }
    except ClientError:
        response = {
            "statusCode": 500,
            "body": "An error occurred while getting all events."
        }

    return response


def get_active(event, context):
    """
    Self-explanatory, retrieves events with "active" status
    :param event:
    :param context:
    :return:
    """
    try:
        active_events = _get_events_by_status('active')

        response = {
            "statusCode": 200,
            "body": json.dumps(active_events)
        }
    except ClientError:
        response = {
            "statusCode": 500,
            "body": "An error occurred while getting active events."
        }

    return response


def get_inactive(event, context):
    """
    Self-explanatory, retrieves events with "inactive" status
    :param event:
    :param context:
    :return:
    """
    try:
        inactive_events = _get_events_by_status('inactive')

        response = {
            "statusCode": 200,
            "body": json.dumps(inactive_events)
        }
    except ClientError:
        response = {
            "statusCode": 500,
            "body": "An error occurred while getting inactive events."
        }

    return response


def get_completed(event, context):
    """
    Self-explanatory, retrieves events with "completed" status
    :param event:
    :param context:
    :return:
    """
    try:
        completed_events = _get_events_by_status('completed')

        response = {
            "statusCode": 200,
            "body": json.dumps(completed_events)
        }
    except ClientError:
        response = {
            "statusCode": 500,
            "body": "An error occurred while getting completed events."
        }

    return response
