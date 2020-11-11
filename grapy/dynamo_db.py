import logging
import os

from boto3 import resource
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING", logging.INFO))


class DynamoDB:
    # adapted from https://gist.github.com/martinapugliese/cae86eb68f5aab59e87332725935fd5f
    def __init__(self):
        self.dynamodb = resource("dynamodb", region_name="eu-west-1")
        self.table_name = os.environ["DYNAMODB_TABLE"]
        self.table = self.dynamodb.Table(self.table_name)

    def ddb_batch_write(self, items):
        self.dynamodb.batch_write_item(
            RequestItems={self.table_name: items}
        )

    def load_dynamo_data(self, data):
        while len(data) > 25:
            self.ddb_batch_write(data[:24])
            data = data[24:]
            logging.info(f"{len(data)} Items left to write...")
        if data:
            self.ddb_batch_write(data)

    def get_table_metadata(self):
        """
        Get metadata about the table.
        """
        return {
            "num_items": self.table.item_count,
            "primary_key_name": self.table.key_schema[0],
            "status": self.table.table_status,
            "bytes_size": self.table.table_size_bytes,
            "global_secondary_indices": self.table.global_secondary_indexes
        }

    @staticmethod
    def _build_key(pk_name, pk_value, sk_name=None, sk_value=None):
        key = {pk_name: pk_value}
        if sk_name:
            key[sk_name] = sk_value
        return key

    def get_item(self, pk_name, pk_value, sk_name=None, sk_value=None):
        """
        Return item read by primary key.
        """
        key = DynamoDB._build_key(pk_name, pk_value, sk_name, sk_value)
        return self.table.get_item(Key=key)

    def add_item(self, col_dict, return_values='NONE'):
        """
        Add one item (row) to table. col_dict is a dictionary {col_name: value}.
        """
        return self.table.put_item(Item=col_dict, ReturnValues=return_values)

    def delete_item(self, pk_name, pk_value, sk_name=None, sk_value=None):
        """
        Delete an item (row) in table from its primary key.
        """
        key = DynamoDB._build_key(pk_name, pk_value, sk_name, sk_value)
        return self.table.delete_item(Key=key)

    def query_table(self, filter_key=None, filter_value=None):
        """
        Perform a query operation on the table. Can specify filter_key (col name) and its value to be filtered. Returns the response.

        :param filter_key:
        :param filter_value:
        :return:
        """
        if filter_key and filter_value:
            filtering_exp = Key(filter_key).eq(filter_value)
            response = self.table.query(KeyConditionExpression=filtering_exp)
        else:
            response = self.table.query()

        return response

    def query_index(self, index_name, pk_name, pk_value, sk_name=None, sk_value=None, start_key=None, limit=1000):
        """
        :param index_name:
        :param pk_name:
        :param pk_value:
        :param sk_name:
        :param sk_value:
        :param start_key:
        :param limit:
        :return:
        """
        filtering_exp = Key(pk_name).eq(pk_value)
        if sk_name and sk_value:
            filtering_exp = filtering_exp & Key(sk_name).eq(sk_value)

        query_kwargs = {
            "IndexName": index_name,
            "KeyConditionExpression": filtering_exp,
            "Limit": int(limit)
        }
        if start_key:
            query_kwargs["ExclusiveStartKey"] = start_key

        return self.table.query(**query_kwargs)
