# Grapy

Vivino wine ratings for online vendors


## Getting started

Make sure that you have an active AWS account and that credentials are setup
warning for cost

Run the following commands to setup the required resources on AWS:

* Create a deployment package
    > sls package

* Deploy the package to AWS
    > sls deploy --stage prod

* Populate the database by invoking the lambdas for the events in the `events` directory: 
    > sls invoke -f vivinoList -p events/wine-types.json --stage prod --log

* Check the results by running the lambda:
    > sls invoke -f grapyAll -p tests/testGrapyAll.json --stage prod --log

* And by invoking the API:
    > curl https://[your-api-id].execute-api.eu-west-1.amazonaws.com/prod/all/wine-types


## Run a spider

Now run a spider as follows

> scrapy crawl bloem --logfile logs/bloem.log


## Get the ratings

Make sure to update the file `algoliasearch.yml` with the correct parameters.

Get Vivino ratings and details

> sls invoke -f grapyNoVintage --stage prod --log
