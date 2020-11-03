# Grapy

Vivino wine ratings for online vendors


Aims to answer the following questions:

* on vivino: which of my favourite online vendors can sell this wine for the lowest price?
* in (online) store: what wine is rated highest? what is the best value for money?
* on the road: where in my neighbourhood are wineries, what are their top-rated wines, what would be the price if I buy them online?


## Getting started

Make sure that you have an active AWS account and that credentials are setup. Depending on your account type and usage, 
costs may apply!


### Setting env variables

Grapy uses the Algolia search engine to search the wine index in the same way that the Vivino website searches for 
wines. To operate Algolia, the following parameters must be set in a .env file: 

    ALGOLIA_APP_ID=
    ALGOLIA_API_KEY=
    ALGOLIA_INDEX=


### Setting up the AWS resources

Run the following commands to initialize the resources on AWS:

Create a deployment package

    > sls package

Deploy the package to AWS

    > sls deploy --stage prod


Make note of the Service Information that is displayed during deployment. You need the api key and endpoints later on 
when operating the spiders.

    service: grapy
    stage: prod
    region: eu-west-1
    stack: grapy-prod
    resources: 33
    api keys:
      grapy-prod-apiKey: [your-api-key]
    endpoints:
      GET - https://[your-api-id].execute-api.eu-west-1.amazonaws.com/prod/{entity}
      PUT - https://[your-api-id].execute-api.eu-west-1.amazonaws.com/prod/vendorwines


### Populate the database

Populate the database by invoking the lambda function `updateEntities`. This function reads all countries, regions, 
wine types, wine styles and grapes from the Vivino API and stores them into the Grapy database. Alternatively, you can 
enable the update-schedule, that was created in Amazon EventBridge during deployment, to periodically update these 
entities in your database. 

    > sls invoke -f updateEntities --stage prod --log


Check the results by running the lambda function `listEntities` which returns a list of all available wine types:

    > sls invoke local -f listEntities --data '{\"pathParameters\":{\"entity\":\"winetypes\"}}' --stage prod --log

This should produce a result similar to:

    [
        {
            "sk": "WINETYPES",
            "pk": "winetypes#1",
            "lastSeen": "2020-11-02 14:53:23 +0000",
            "data": "Red Wine"
        },
        {
            "sk": "WINETYPES",
            "pk": "winetypes#2",
            "lastSeen": "2020-11-02 14:53:23 +0000",
            "data": "White Wine"
        },
        ...omitted...
    ]


Alternatively, you can list the entities by calling the Rest API:

    > curl -X GET -H "x-api-key: [your-api-key]" https://[your-api-id].execute-api.eu-west-1.amazonaws.com/prod/winetypes


## Running a spider

Before running a spider, make sure to set the environment variables `DYNAMODB_ENDPOINT` and `DYNAMODB_API_KEY` to match 
the AWS resources that were created earlier. Any scraped vendor wines can now be stored in the Grapy database.

Run a spider as follows:

    > scrapy crawl bloem --logfile logs/bloem.log --loglevel INFO

Wines that are found on the website of [Henri Bloem] are scraped and stored in the Grapy database.


## Get the ratings

The next step is to search Vivino for the wines that we just scraped from the wine vendor's website. This process can 
be started manually by invoking:

    > sls invoke -f vivinofy --stage prod --log

Resulting in

    {
        "statusCode": 200,
        "body": "10 Vendor wines updated, 36 remaining"
    }

Alternatively, you can enable the search-schedule that was created in Amazon EventBridge during deployment, to 
periodically search for unmatched vendor wines in your database. 


## Getting the result from the database

To get the results from the database you can invoke the API:

    > curl -X GET -H "x-api-key: [your-api-key]" https://[your-api-id].execute-api.eu-west-1.amazonaws.com/prod/vendorwines

Which results in a list of vendor wines:

    [
      {
        "winery": "Ch\u00e2teau Pigoudet",
        "lastSeen": "2020-11-03 10:07:56 +0000",
        "data": "vintages#",
        "year": "2019",
        "sk": "VENDORWINES",
        "volume": 0.75,
        "price": 10.95,
        "pk": "vendorwines#https://www.henribloem.nl/177244_Chateau-Pigoudet_Cuvee-Classic.html",
        "vendor": {
          "name": "Henri Bloem",
          "url": "henribloem.nl"
        },
        "name": "Cuv\u00e9eClassic"
      },
      ...omitted...
    ]


## Adding a new spider

Run the following scrapy command to create a new spider from the vendor template:

    > scrapy genspider -t vendor [name] [domain]

This creates an new spider in the vendors/spiders directory. Modify to scrape wine fields.

Run it with output to file (TODO: should disable AWS output)

    > scrapy crawl [name] -o test.csv --logfile test.log --loglevel DEBUG


## Interpreting the data model
Todo


## Admin and dev stuff

* Install dependencies

    > pip install -r requirements.txt

* Run tests (make sure env variables are set ALGOLIA_APP_ID)

    > python -m pytest

* Remove the stack and resources; Warning: deletes all data (except in prod?)

    > sls remove


## Future work

- use dedicated AWS account for project
- modify Vivinofy so that it doesn't loop forever on wines that have no match
- modify attrs to lastSeenAtVendor and lastSeenAtVivino
- improve spider tests by using [Scrapy spider contracts]


[Henri Bloem]: https://www.henribloem.nl/ 
[Scrapy spider contracts]: https://docs.scrapy.org/en/latest/topics/contracts.html