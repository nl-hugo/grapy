# Grapy

Vivino wine ratings for online vendors


## Getting started

make sure you have an active AWS account [ref?]
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


