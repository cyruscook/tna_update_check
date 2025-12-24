# requirements: boto3

import json
import logging
import os

import boto3
import requests
from requests.adapters import HTTPAdapter

from check.check import check_records
from website.handler import handle_web_request

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOGLEVEL", "INFO").upper())


def lambda_handler(event, context):
    try:
        LOGGER.debug(
            "Lambda invoked",
            extra={
                "event": json.dumps(event, default=repr),
                "context": json.dumps(context, default=repr),
            },
        )

        s3 = boto3.client("s3")
        sns = boto3.client("sns")
        lamc = boto3.client("lambda")
        sess = requests.Session()
        sess.mount("https://", HTTPAdapter(max_retries=2))
        sess.headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
        )

        furl = lamc.get_function_url_config(FunctionName=context.function_name)[
            "FunctionUrl"
        ]

        if "requestContext" in event and "http" in event["requestContext"]:
            # HTTP Request
            LOGGER.debug("handling web request")
            return handle_web_request(sess, s3, event)
        elif "action" in event and event["action"] == "check":
            # Check records
            LOGGER.debug("checking records")
            check_records(sess, s3, sns, furl)
            LOGGER.info("successfully checked records")
        else:
            raise Exception("Unknown action")
    except Exception as e:
        LOGGER.exception("Error handling lambda invocation")
        raise e


if __name__ == "__main__":
    lambda_handler({}, {})
