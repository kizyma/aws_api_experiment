import boto3


def create_event_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

    table_name = 'events'
    params = {
        'TableName': table_name,
        'KeySchema': [
            {'AttributeName': 'event_id', 'KeyType': 'HASH'}
        ],
        'AttributeDefinitions': [
            {'AttributeName': 'event_id', 'AttributeType': 'N'},
            {'AttributeName': 'status', 'AttributeType': 'S'},
            # {'AttributeName': 'end_date', 'AttributeType': 'S'},
            {'AttributeName': 'timestamp', 'AttributeType': 'N'},
        ],
        'GlobalSecondaryIndexes': [
            {
                'IndexName': 'statusTimestampIndex',
                'KeySchema': [
                    {'AttributeName': "status", 'KeyType': "HASH"},
                    {'AttributeName': "timestamp", 'KeyType': "RANGE"}
                ],
                # 'AttributeDefinitions': [
                #     {'AttributeName': "status", 'AttributeType': "S"},
                #     {'AttributeName': "timestamp", 'AttributeType': "N"}
                # ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            }
        ],

        'ProvisionedThroughput': {
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    }
    table = dynamodb.create_table(**params)
    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    assert table.table_status == 'ACTIVE'
    return table
