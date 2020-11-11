import json
import logging
import urllib.parse
from decimal import Decimal
from functools import wraps

from grapy import decimalencoder, grapy, grapy_db

logger = logging.getLogger()


def as_lambda(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        logger.info(f"Received event \"{f.__name__}\" -- {args}")
        response = f(*args, **kwargs)
        return {
            "statusCode": 200,
            "body": json.dumps(response, cls=decimalencoder.DecimalEncoder)
        }

    return wrapper


@as_lambda
def update_all(event, context):
    # sls invoke local -f update
    grapy_db.GrapyDDB().populate()
    return "GrapyDB populated."


@as_lambda
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
    return {
        "data": data,
        "count": res.get("Count"),
        "nextPage": next_page_url
    }


@as_lambda
def add_vendor_wine(event, context):
    """ Adds a vendor wine to the Grapy database. """
    # to be used by scrapy to hand in newly scraped vendor wines
    # sls invoke local -f add -p tests/fixtures/vendorwine.json
    # float has to be translated to Decimal
    item = json.loads(event.get("body"), parse_float=Decimal)
    return grapy_db.GrapyDDB().add_vendor_wine(item)


@as_lambda
def vivinofy(event, context):
    """ Gets all vendor wines without vintage and searches Vivino for details. Results are stored in the Grapy
    database. """
    upd, rem = grapy.Grapy().vivinofy()
    return f"{upd} Vendor wines updated, {rem} remaining"
