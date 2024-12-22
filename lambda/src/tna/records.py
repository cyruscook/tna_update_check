import requests
import urllib.parse

from tna.constants import (
    TNA_API,
    TNA_RECORD_DETAILS,
    TNA_RECORDS_DETAILS,
    TNA_RECORDS_COLLECTION,
)


def get_record_by_id(sess: requests.Session, id: str):
    resp = sess.get(
        f"{TNA_API}{TNA_RECORDS_DETAILS}".format(id=urllib.parse.quote(id, safe=""))
    )
    resp.raise_for_status()
    resp = resp.json()
    return resp


def get_record_by_ref(sess: requests.Session, ref: str) -> object:
    resp = sess.get(
        f"{TNA_API}{TNA_RECORDS_COLLECTION}".format(
            reference=urllib.parse.quote(ref, safe="")
        )
    )
    resp.raise_for_status()
    resp = resp.json()
    assets = resp["assets"]
    if len(assets) != 1:
        raise Exception("Incorrect number of assets")
    return assets[0]


def get_link_by_id(id: str) -> str:
    return TNA_RECORD_DETAILS.format(id=urllib.parse.quote(id, safe=""))
