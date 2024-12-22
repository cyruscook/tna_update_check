# requirements: boto3

import requests
import os
import logging
import json
import boto3

from website.handler import handle_web_request

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOGLEVEL", "INFO").upper())


def lambda_handler(event, context):
    LOGGER.debug("Handler event=%s context=%s", json.dumps(event, default=repr), json.dumps(context, default=repr))

    s3 = boto3.client("s3")
    sns = boto3.client("sns")
    sess = requests.Session()

    if "requestContext" in event and "http" in event["requestContext"]:
        # HTTP Request
        return handle_web_request(sess, s3, event)
    elif "action" in event and event["action"] == "check":
        # Check records
        pass
    else:
        LOGGER.error("Unknown action")
        raise Exception("Unknown action")


if __name__ == "__main__":
    lambda_handler({}, {})
