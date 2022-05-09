region := "<your_region>"
endpoint_uri := "<your_lambda_endpoint_uri>"
repo_uri := "<your_ecr_repository_uri>"
image_name := "emojifinder"

default:
    @just --list

auth:
    account_id=$(aws sts get-caller-identity --query Account --output text) \
    && aws ecr get-login-password | docker login --username AWS --password-stdin ${account_id}.dkr.ecr.{{region}}.amazonaws.com

deploy:
    docker build -t {{image_name}} . --platform=linux/amd64
    docker tag {{image_name}} {{repo_uri}}
    docker push {{repo_uri}}
    serverless deploy

query query n="16":
    @curl -s -X POST {{endpoint_uri}} -d '{"query": "{{query}}", "n": {{n}}}'

emojis query n="16":
    @just query "{{query}}" "{{n}}" | jq -r .emojis[].symbol | tr '\n' ' '
