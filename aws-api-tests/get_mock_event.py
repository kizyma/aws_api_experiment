from pprint import pprint
import boto3
from botocore.exceptions import ClientError


def get_event(event_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('events')

    try:
        response = table.get_item(TableName='events', Key={'event_id': event_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Item']


if __name__ == '__main__':
    event = get_event(1)
    if event:
        print("Get event succeeded:")
        pprint(event, sort_dicts=False)
