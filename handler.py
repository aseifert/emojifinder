import json
from dataclasses import asdict
from functools import lru_cache

from loguru import logger
from sentence_transformers import SentenceTransformer

from emojifinder import Emoji, find_emoji, get_vectors


@lru_cache
def get_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


@lru_cache
def get_emojis() -> list[Emoji]:
    with open("emoji-en-US.json") as fp:
        return [Emoji(k, v) for k, v in json.load(fp).items()]


def endpoint(event, context):
    logger.info(event)

    try:
        request = json.loads(event["body"])
        query = request.get("query")
        assert query, f"`query` is required"
        n = int(request.get("n", 32))

        model = get_model("model/")
        emojis = get_emojis()
        embeddings = get_vectors(model, emojis)

        response = {
            "emojis": [
                asdict(e)
                for e in find_emoji(
                    query=query, emojis=emojis, model=model, embeddings=embeddings, n=n
                )
            ]
        }

        # https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-integration-settings-integration-response.html
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps(response),
        }
    except Exception as e:
        logger.error(repr(e))

        # https://docs.aws.amazon.com/apigateway/latest/developerguide/handle-errors-in-lambda-integration.html
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps({"error": repr(e), "event": event, "context": context}),
        }


if __name__ == "__main__":
    print(endpoint({"body": json.dumps({"query": "vacation", "n": 3})}, None)["body"])
