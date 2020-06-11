import logging
import os

from algoliasearch.search_client import SearchClient

client = SearchClient.create(os.environ['ALGOLIA_APP'], os.environ['ALGOLIA_KEY'])
index = client.init_index(os.environ['ALGOLIA_INDEX'])

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_year(item):
    return item['year']


def search_vintage(event, context):
    logging.info('Searching for {}'.format(event))
    keywords = event.get('keywords')
    year = event.get('year', 'U.V.')

    res = index.search(keywords, {
        'attributesToRetrieve': [
            'id',
            'name',
            'type_id',
            'style_id',
            'region.id',
            'grapes',
            'winery.id',
            'vintages.id',
            'vintages.year',
        ],
        # 'filters': filters,
        'hitsPerPage': 1
    })
    hits = res['hits']

    if hits and len(hits) > 0:
        logging.info('{} Results'.format(len(hits)))
        result = hits[0]
        vintages = result['vintages']

        # get year in correct format, if  no year then N.V.
        vintage = sorted([v for v in vintages if v['year'] == year or v['year'] == 'U.V.'], key=get_year)

        # response should contain the vintage ID from vivino search (and additional elts)
        del result['_highlightResult']
        result['vintages'] = vintage[0]

        return {
            'statusCode': 200,
            'body': result
        }
    else:
        return {
            'statusCode': 200,
            'body': 'No results for {}'.format(keywords)
        }
