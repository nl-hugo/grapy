# Adapted from https://github.com/trek10inc/ddb-single-table-example
import copy
from time import localtime, strftime

from grapy.vivino_api import VivinoApi


def build_node_list(node_rows, pk, sk, gs1_sk):
    partition = []
    for row in node_rows:
        node_row = build_node(row, pk, sk, gs1_sk)
        partition.append({'PutRequest': {'Item': node_row}})
    return partition


def build_node(row, pk, sk, gs1_sk):
    node_row = copy.deepcopy(row)
    node_row["pk"] = f"{sk.lower()}#{str(node_row.pop(pk, pk))}"
    node_row["sk"] = str(node_row.pop(sk, sk))
    node_row["data"] = build_composite_sort_key(node_row, gs1_sk)
    node_row["lastSeen"] = strftime("%Y-%m-%d %H:%M:%S %z", localtime())
    return node_row


def build_composite_sort_key(row, keyname):
    elements = keyname.split("#")
    key = [str(row.pop(element, element)) for element in elements]
    return "#".join(key)


def build_adjacency_lists(countries, regions, wine_types, wine_styles, grapes):
    adjacency_lists = build_node_list(countries, "code", "COUNTRIES", "name")
    adjacency_lists += build_node_list(regions, "id", "REGIONS", "countries#country")
    adjacency_lists += build_node_list(wine_types, "id", "WINETYPES", "name")
    adjacency_lists += build_node_list(wine_styles, "id", "WINESTYLES", "name")
    adjacency_lists += build_node_list(grapes, "id", "GRAPES", "name")
    return adjacency_lists


def load_data():
    vivino = VivinoApi()
    countries = vivino.get_countries()
    regions = vivino.get_regions()
    wine_types = vivino.get_wine_types()
    wine_styles = vivino.get_wine_styles()
    grapes = vivino.get_grapes()

    return countries, regions, wine_types, wine_styles, grapes
