import logging
import boto3
import datetime
import simplejson as json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
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

ALL_AVAILABLE_STATUSES = ['active', 'inactive', 'completed']


def create(event, context) -> json:
    """
    Function to create event from user input. In case some optional fields are missing - fill them out via pydantic.
    For more info on data model, validation and data serialization, please consult pydantic_datamodel module.
    :param event:
    :param context:
    :return: response, notifies user about the result of the operation
    """
    logger.info(f'Incoming request is: {event}')
    response = {
        "statusCode": 400,
        "body": "An error occurred while creating post. Please make sure incoming event has event_id field."
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
                "body": "New data entry has been added successfully."
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


def _get_all() -> json:
    """
    Function to retrieve all events. Make several calls, to get all known event statuses and then return unified list
    :return: response with all lists
    """
    try:
        all_events = []
        for status in ALL_AVAILABLE_STATUSES:
            event_list = _get_events_by_status(status)
            all_events += event_list
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


def get_by_status(events, context) -> json:
    """
    :param events: receive parameter to parse and retrieve from event
    :param context:
    :return: json-response to a user, no aux./service fields
    """
    try:
        status = events.get('pathParameters', {}).get('status_param')
    except (TypeError, AttributeError):
        status = None

    if status:
        try:
            selected_events = _get_events_by_status(status)
            response = {
                "statusCode": 200,
                "body": json.dumps(selected_events)
            }
        except ClientError:
            response = {
                "statusCode": 500,
                "body": "An error occurred while getting selected events."
            }
    elif status is None:
        response = _get_all()
    return response
