import urllib.parse
from typing import Any

import requests

from tna.constants import (
    TNA_API,
    TNA_RECORD_DETAILS,
    TNA_RECORDS_COLLECTION,
    TNA_RECORDS_DETAILS,
)

REQ_TIMEOUT = 30  # 30 seconds


def get_record_by_id(sess: requests.Session, id: str) -> Any:
    resp = sess.get(
        f"{TNA_API}{TNA_RECORDS_DETAILS}".format(id=urllib.parse.quote(id, safe="")),
        timeout=REQ_TIMEOUT,
    )
    resp.raise_for_status()
    resp = resp.json()
    return resp


def get_record_by_ref(sess: requests.Session, ref: str) -> Any:
    resp = sess.get(
        f"{TNA_API}{TNA_RECORDS_COLLECTION}".format(
            reference=urllib.parse.quote(ref, safe="")
        ),
        timeout=REQ_TIMEOUT,
    )
    resp.raise_for_status()
    resp = resp.json()
    assets = resp["assets"]
    if len(assets) != 1:
        raise Exception("Incorrect number of assets")
    return assets[0]


def get_link_by_id(id: str) -> str:
    return TNA_RECORD_DETAILS.format(id=urllib.parse.quote(id, safe=""))
