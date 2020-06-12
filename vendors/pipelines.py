# -*- coding: utf-8 -*-

import logging
import os
from decimal import Decimal
from time import localtime, strftime

import boto3
from botocore.exceptions import ClientError
from scrapy.conf import settings
from scrapy.exceptions import DropItem


def is_in_aws():
    return os.getenv('AWS_EXECUTION_ENV') is not None


class WineVendorsPipeline(object):
    required_fields = [
        'url',
        'name'
    ]  # required fields

    forbidden_names = [
        'proefdoos',
        'pakket',
        'giftbox',
        'cadeau'
    ]  # anti-names

    def __init__(self):
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        if is_in_aws():
            self.table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
        else:
            self.table = dynamodb.Table(settings['DYNAMODB_TABLE'])

    def validate(self, item):
        valid = False

        # better to be too strict, to avoid dirty data
        for data in item:
            if not data:
                raise DropItem('Missing {}'.format(data))

        # must not contain forbidden name
        for name in self.forbidden_names:
            if name in item['name'].lower():
                raise DropItem('Forbidden name {}'.format(name))

        # price greater than zero
        if item['price'] <= 0:
            raise DropItem('Price too low {}'.format(item['price']))

        # acceptable volumes
        if item['volume'] not in [.375, .5, .75, 1, 1.5, 2.25, 3, 6]:
            raise DropItem('Volume {} not acceptable'.format(item['volume']))

        # set year if missing
        if item['year'] is None:
            logging.warning('Vintage missing, set to U.V.')
            item['year'] = 'U.V.'

        # TODO: does validate return when dropping an item?
        valid = True
        return valid

    def get_item(self, item):
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

    def create_item(self, item):
        now = strftime('%Y-%m-%d %H:%M:%S %z', localtime())
        try:
            self.table.put_item(Item={
                'pk': item['url'],
                'sk': 'VENDORWINE',
                'data': 'vintages#',
                'name': item['name'],
                'vendor': item['vendor'],
                'winery': item['winery'],
                'year': item['year'],
                'price': Decimal(str(item['price'])),
                'volume': Decimal(str(item['volume'])),
                'firstSeen': now,
                'lastSeen': now,
            })
        except ClientError as e:
            logging.error(e.response['Error']['Message'])

    def update_item(self, item):
        # only update price and date updated
        now = strftime('%Y-%m-%d %H:%M:%S %z', localtime())
        try:
            self.table.update_item(
                Key={
                    'pk': item['url'],
                    'sk': 'VENDORWINE',
                },
                UpdateExpression='set price=:p, volume=:v, lastSeen=:n',
                ExpressionAttributeValues={
                    ':p': Decimal(str(item['price'] or 0.0)),
                    ':v': Decimal(str(item['volume'] or 0.0)),
                    ':n': now
                },
            )
        except ClientError as e:
            logging.error(e.response['Error']['Message'])

    def process_item(self, item, spider):
        if self.validate(item):
            response = self.get_item(item)
            if response:
                self.update_item(item)
            else:
                self.create_item(item)

        return item
