from pprint import pprint
from utils.pydantic_datamodel import convert_string_to_dt_object
import boto3
from botocore.exceptions import ClientError


def put_event(event_id, event_name, status, start_date, end_date, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('events')
    response = table.put_item(
        Item={
            'event_id': event_id,
            'event_name': event_name,
            'status': status,
            'start_date': start_date,
            'end_date': end_date
        }
    )
    return response


if __name__ == '__main__':
    movie_resp = put_event(1, "Generic Test Event", "completed", convert_string_to_dt_object("2021-12-06 17:27:04"),
                           convert_string_to_dt_object("2021-12-06 18:27:04"), 0)
    print("Put event succeeded:")
    pprint(movie_resp, sort_dicts=False)
