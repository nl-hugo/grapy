import json
import logging
import os

import boto3

from lambdas import decimalencoder, utils

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
lambda_client = boto3.client('lambda', region_name='eu-west-1')

table_name = os.environ['DYNAMODB_TABLE']


def build_node_list(node_rows, pk, sk, gs1_sk, keep=None):
    partition = []
    _keep = [pk, gs1_sk]

    if keep is not None and isinstance(keep, list):
        _keep += keep

    for row in node_rows:
        node_row = {}
        for k in _keep:
            node_row[k] = utils.safe_get(row, k.split('.'))
        node_row['pk'] = build_composite_sort_key(node_row, pk, sk)
        node_row['sk'] = node_row.pop(sk, sk).upper()
        node_row['data'] = node_row.pop(gs1_sk, gs1_sk)
        partition.append({'PutRequest': {'Item': node_row}})
    return partition


def build_composite_sort_key(row, pk, key_name):
    key = row.pop(pk, pk)
    return '#'.join([key_name, str(key)])


def ddb_batch_write(items):
    dynamodb.batch_write_item(
        RequestItems={table_name: items}
    )


def load_dynamo_data(data):
    logging.info('Loading {} items into {}'.format(len(data), table_name))
    while len(data) > 25:
        ddb_batch_write(data[:24])
        data = data[24:]
    if data:
        ddb_batch_write(data)


def add_winery(winery_id):
    logging.info('Add winery {} to {}'.format(winery_id, table_name))
    lambda_client.invoke(
        FunctionName='{}-vivinoGet'.format(table_name),
        InvocationType='RequestResponse',
        Payload=json.dumps({
            'entity': 'wineries',
            'id': winery_id,
            'pk': 'id',
            'gs1_sk': 'name',
            'keep': [
                'region.id',
                'website',
                'location'
            ]
        }, cls=decimalencoder.DecimalEncoder)
    )


def add_vintage(vintage_id):
    logging.info('Add vintage {} to {}'.format(vintage_id, table_name))
    lambda_client.invoke(
        FunctionName='{}-vivinoGet'.format(table_name),
        InvocationType='RequestResponse',
        Payload=json.dumps({
            'entity': 'vintages',
            'id': vintage_id,
            'pk': 'id',
            'gs1_sk': 'name',
            'keep': [
                'wine.id',
                'year',
                'statistics.ratings_count',
                'statistics.ratings_average'
            ]
        }, cls=decimalencoder.DecimalEncoder)
    )
