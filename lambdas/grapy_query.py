import json
import logging
import os

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from lambdas import decimalencoder, utils, grapy_ddb

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
lambda_client = boto3.client('lambda', region_name='eu-west-1', )

table_name = os.environ['DYNAMODB_TABLE']
table = dynamodb.Table(table_name)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def no_vintage(event, context):
    """
    Gets all VendorWine objects without a vintage and searches Vivino for a suitable match.
    :param event:
    :param context:
    :return:
    """
    # TODO: this function should be scheduled by cron
    # TODO: paginate?
    # TODO: top-10?
    # TODO: oldest first?
    result = table.query(IndexName='gsi_1',
                         KeyConditionExpression=Key('sk').eq('VENDORWINE') & Key('data').eq('vintages#'))

    logging.debug(result)
    items = result['Items']
    counter = 0

    for res in items[:10]:
        counter = counter + 1

        # get keywords to search
        wine = res['name']
        winery = res['winery']
        year = res['year']
        keywords = '{} {}'.format(winery, wine)  # TODO: remove duplicate terms

        logging.info('Searching vintage {} for keywords {}'.format(year, keywords))

        # sends the search request
        response = lambda_client.invoke(
            FunctionName='{}-vivinoSearch'.format(table_name),
            InvocationType='RequestResponse',
            Payload=json.dumps({'keywords': keywords, 'year': year})
        )

        # response should contain the vintage ID from vivino search (and additional elts)
        string_response = response['Payload'].read().decode('utf-8')
        logging.debug(string_response)

        data = json.loads(string_response)['body']
        logging.debug(data)

        # from the response, we should create a wine, vintage, winery object
        # search and store winery (lambda)
        winery_id = utils.safe_get(data, ['winery', 'id'])
        if winery_id:
            grapy_ddb.add_winery(winery_id)

        # search and store vintage (lambda)
        vintage_id = utils.safe_get(data, ['vintages', 'id'])
        if vintage_id:
            grapy_ddb.add_vintage(vintage_id)

        # create wine object ()
        logging.info('Add wine {}'.format(data['id']))
        table.put_item(Item={
            'pk': 'wines#' + str(data['id']),
            'sk': 'WINES',
            'data': data['name'],
            'winery': str(winery_id),  # winery.id ??
            'type': str(data.get('type_id', '')),
            'style': str(data.get('style_id', '')),
            'grapes': data.get('grapes')
        })

        # and update the original vendor wine to match the vintageId
        # update vendorwine object ()
        res['data'] = 'vintages#{}'.format(data['vintages']['id'])

        logging.info('Update vendorwine {} with vintage {}'.format(data['id'], res['data']))
        try:
            table.put_item(Item=res)
        except ClientError as e:
            logging.error('Error {}'.format(e.response['Error']['Message']))

    return {
        'statusCode': 200,
        'body': '{} items updated, {} left to update'.format(counter, max(0, len(items) - 10))  # TODO: better message
    }


def get_all(event, context):
    """
    Gets all entities from the database
    :param event:
    :param context:
    :return:
    """
    entity = event['pathParameters']['entity']
    logging.info('Getting all {}'.format(entity))
    if entity:
        # TODO: paginate
        result = table.query(IndexName='gsi_1', KeyConditionExpression=Key('sk').eq(entity.upper()))
        return {
            'statusCode': 200,
            'body': json.dumps(result['Items'], cls=decimalencoder.DecimalEncoder)
        }
