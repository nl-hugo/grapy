import json
import logging
from decimal import Decimal

import requests

from lambdas import grapy_ddb

base_url = 'http://api.vivino.com/'

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_all(event, context):
    """
    Lists all entities
    :param event:
    :param context:
    :return:
    """
    entity = event['entity']
    response = __query_api__(entity)

    if event.get('get_detailed_info') is True:
        for i, key in enumerate(
                r.get(event['pk']) for r in response if r.get('has_detailed_info') is True and r.get(event['pk'])):
            response[i] = __query_api__(entity, key=key)

    table_data = grapy_ddb.build_node_list(response, event['pk'], entity, event['gs1_sk'], keep=event.get('keep'))
    grapy_ddb.load_dynamo_data(table_data)

    return {
        'statusCode': 200,
        'body': '{} {} added'.format(len(response), entity)
    }


def get_item(event, context):
    """
    Gets one entity by id
    :param event:
    :param context:
    :return:
    """
    entity = event['entity']
    response = __query_api__(entity, event['id'])

    table_data = grapy_ddb.build_node_list([response], event['pk'], entity, event['gs1_sk'], keep=event.get('keep'))
    # TODO: no need to do a batch write + remove permissions from sls.yml too!
    grapy_ddb.load_dynamo_data(table_data)

    return {
        'statusCode': 200,
        'body': '{} {} added'.format(len(response), entity)
    }


def __query_api__(entity, key=None):
    url = '{}{}{}'.format(base_url, entity, '/' + str(key) if key else '')
    logging.debug('Querying {}'.format(url))

    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        return json.loads(response.text, parse_float=Decimal)
    else:
        response.raise_for_status()
