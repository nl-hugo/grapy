import json
from decimal import Decimal

from grapy import decimalencoder, grapy, grapy_db


def update_all(event, context):
    # sls invoke local -f update
    grapy_db.GrapyDDB().populate()
    return {
        "statusCode": 200,
        "body": "success"
    }


def list_all(event, context):
    """ Lists all items for the specified entity. """
    # sls invoke local -f listEntities --data '{\"pathParameters\":{\"entity\":\"winetypes\"}}'
    entity = event["pathParameters"]["entity"]
    res = grapy_db.GrapyDDB().get_all(entity)
    return {
        "statusCode": 200,
        "body": json.dumps(res.get("Items"), cls=decimalencoder.DecimalEncoder)
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
