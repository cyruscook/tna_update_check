# requirements: boto3

import requests
from requests.adapters import HTTPAdapter
import os
import logging
import json
import boto3

from website.handler import handle_web_request
from check.check import check_records

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOGLEVEL", "INFO").upper())


def lambda_handler(event, context):
    LOGGER.debug(
        "Handler event=%s context=%s",
        json.dumps(event, default=repr),
        json.dumps(context, default=repr),
    )

    s3 = boto3.client("s3")
    sns = boto3.client("sns")
    lamc = boto3.client("lambda")
    sess = requests.Session()
    sess.mount("https://", HTTPAdapter(max_retries=2))
    sess.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"

    furl = lamc.get_function_url_config(FunctionName=context.function_name)[
        "FunctionUrl"
    ]

    if "requestContext" in event and "http" in event["requestContext"]:
        # HTTP Request
        return handle_web_request(sess, s3, event)
    elif "action" in event and event["action"] == "check":
        # Check records
        check_records(sess, s3, sns, furl)
    else:
        LOGGER.error("Unknown action")
        raise Exception("Unknown action")


if __name__ == "__main__":
    lambda_handler({}, {})
