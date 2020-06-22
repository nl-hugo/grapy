# -*- coding: utf-8 -*-

import logging
import os
from decimal import Decimal
from time import localtime, strftime

import boto3
from botocore.exceptions import ClientError
from scrapy.conf import settings


def is_in_aws():
    return os.getenv('AWS_EXECUTION_ENV') is not None


class WineVendorsPipeline(object):

    def __init__(self):
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        if is_in_aws():
            self.table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
        else:
            self.table = dynamodb.Table(settings['DYNAMODB_TABLE'])

    def get_item(self, item):
        logging.debug('Get item {}'.format(item))
        try:
            response = self.table.get_item(
                Key={
                    'pk': item['url'],
                    'sk': 'VENDORWINE'
                })
        except ClientError as e:
            logging.error(e.response['Error']['Message'])
        else:
            if 'Item' in response:
                return response['Item']

    def create_item(self, item, first_seen=None):
        logging.debug('Create item {}, first seen at {}'.format(item, first_seen))
        now = strftime('%Y-%m-%d %H:%M:%S %z', localtime())
        try:
            response = self.table.put_item(Item={
                'pk': item['url'],
                'sk': 'VENDORWINE',
                'data': 'vintages#',
                'name': item['name'],
                'vendor': item['vendor'],
                'winery': item['winery'],
                'year': item['year'],
                'price': Decimal(str(item['price'])),
                'volume': Decimal(str(item['volume'])),
                'firstSeen': first_seen or now,
                'lastSeen': now,
            })
        except ClientError as e:
            logging.error(e.response['Error']['Message'])
        else:
            return self.get_item(item)

    def update_item(self, item):
        now = strftime('%Y-%m-%d %H:%M:%S %z', localtime())
        try:
            response = self.table.update_item(
                Key={
                    'pk': item['url'],
                    'sk': 'VENDORWINE',
                },
                UpdateExpression='set vendor=:vd, price=:p, volume=:v, lastSeen=:n',
                ExpressionAttributeValues={
                    ':vd': item['vendor'],
                    # ':vt': ':data' + '#test',
                    ':p': Decimal(str(item['price'])),
                    ':v': Decimal(str(item['volume'])),
                    ':n': now
                },
            )
        except ClientError as e:
            logging.error(e.response['Error']['Message'])
        else:
            return self.get_item(item)

    def delete_item(self, item):
        logging.debug('Delete item {}'.format(item))
        try:
            response = self.table.delete_item(
                Key={
                    'pk': item.get('url'),
                    'sk': 'VENDORWINE'
                },
                ReturnValues='ALL_OLD',
            )
        except ClientError as e:
            logging.error(e.response['Error']['Message'])
        else:
            if 'Attributes' in response:
                return response.get('Attributes')

    def process_item(self, item, spider):
        logging.debug('Process item {}'.format(item))
        result = None
        item.validate()

        # see if the item already exists
        result = self.get_item(item)

        if not result:
            result = self.create_item(item)
        else:
            # see if the item needs to be recreated, if
            # any of the fields wine, winery or year has changed
            needs_recreate = result.get('name') != item.get('name') or \
                             result.get('winery') != item.get('winery') or \
                             result.get('year') != item.get('year')
            if needs_recreate:
                # wine, winery or year --> clear vintage#id
                # vendor, price, volume --> ok, update
                # pk, sk, data (url, VW, vintages#), firstSeen never update
                # always update lastSeen
                self.delete_item(item)
                result = self.create_item(item, first_seen=result.get('firstSeen'))
            else:
                result = self.update_item(item)

        return result
