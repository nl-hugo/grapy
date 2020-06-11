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

        # for data in item:
        #     if not data:
        #         valid = False
        #         raise DropItem('Missing {0}!'.format(data))
        # TODO: improve validation
        # TODO: check data types
        if not all(field in item for field in self.required_fields):
            print('dropped missing {}'.format(item['url']))
            raise DropItem('Required field missing: {}'.format(item))
        elif any(name in item['name'].lower() for name in self.forbidden_names):  # TODO: contains, ignore case
            print('dropped forbidden {}'.format(item['url']))
            raise DropItem('Forbidden name: {}'.format(item))
        else:
            return True

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
                'year': item['year'] or 'U.V.',
                'price': Decimal(str(item['price'] or 0.0)),  # FIXME: fails if price is None, or updates to 0 sometimes
                'volume': Decimal(str(item['volume'] or 0.0)),
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
