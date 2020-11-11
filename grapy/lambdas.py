import json
import logging
import urllib.parse
from decimal import Decimal

from grapy import decimalencoder, grapy, grapy_db

logger = logging.getLogger()


def update_all(event, context):
    # sls invoke local -f update
    grapy_db.GrapyDDB().populate()
    return {
        "statusCode": 200,
        "body": "success"
    }


def list_all(event, context):
    """ Lists all items for the specified entity. """
    # sls invoke local -f listTable --data '{\"pathParameters\":{\"table\":\"countries\"},\"queryStringParameters\":{\"pk\":\"countries#ar\",\"sk\":\"COUNTRIES\",\"data\":\"Argentina\",\"limit\":10}}'
    logger.info(f"Paginate {event}")

    # TODO: find more elegant way to extract parameters
    table_name = event["pathParameters"]["table"]
    logger.info(f"table_name: {type(table_name)} -- {table_name}")

    query_params = event["queryStringParameters"]
    logger.info(f"query_params: {type(query_params)} -- {query_params}")

    limit = query_params.pop("limit", None)
    res = grapy_db.GrapyDDB().get_all(table_name, query_params, limit)
    logger.info(f"res: {type(res)} -- {res}")

    # get the last evaluated key from the response
    next_page_url = None
    last_key = res.get("LastEvaluatedKey")
    if last_key:
        last_key["limit"] = limit
        domain_name = event["requestContext"]["domainName"]
        path = event["requestContext"]["path"]
        qs = urllib.parse.urlencode(last_key)
        next_page_url = f"https://{domain_name}{path}?{qs}"

    data = res.get("Items", [])
    response = {
        "data": data,
        "count": res.get("Count"),
        "nextPage": next_page_url
    }
    return {
        "statusCode": 200,
        "body": json.dumps(response, cls=decimalencoder.DecimalEncoder)
    }


def add_vendor_wine(event, context):
    """ Adds a vendor wine to the Grapy database. """
    # to be used by scrapy to hand in newly scraped vendor wines
    # sls invoke local -f add -p tests/fixtures/vendorwine.json
    # float has to be translated to Decimal
    item = json.loads(event.get("body"), parse_float=Decimal)
    res = grapy_db.GrapyDDB().add_vendor_wine(item)
    return {
        "statusCode": 200,
        "body": json.dumps(res)
    }


def vivinofy(event, context):
    """ Gets all vendor wines without vintage and searches Vivino for details. Results are stored in the Grapy
    database. """
    upd, rem = grapy.Grapy().vivinofy()
    return {
        "statusCode": 200,
        "body": f"{upd} Vendor wines updated, {rem} remaining"
    }
