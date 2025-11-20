import json
import logging
import os
import urllib.parse
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, List, TypeAlias

import requests

from check.alert import publish_change
from storage.monitored import get_monitored_records, put_monitored_records
from storage.redirs import put_redir
from tna.records import get_link_by_id, get_record_by_id

JDIFF = "https://benjamine.github.io/jsondiffpatch/index.html?desc=diff&left={left}&right={right}"

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOGLEVEL", "INFO").upper())

CheckRecordResult: TypeAlias = tuple[Any, tuple[str, str] | None]


def check_record(sess: requests.Session, record: Any) -> CheckRecordResult:
    id = record["id"]
    newr = get_record_by_id(sess, id)
    oldj = json.dumps(record, sort_keys=True)
    newj = json.dumps(newr, sort_keys=True)
    if oldj == newj:
        return (newr, None)
    return (newr, (oldj, newj))


def alert_for_record(s3, furl: str, record: Any, oldj: str, newj: str) -> str:
    id = record["id"]
    ref = record["citableReference"]
    catlink = get_link_by_id(id)
    difflink = JDIFF.format(
        left=urllib.parse.quote(oldj), right=urllib.parse.quote(newj)
    )
    redirkey = put_redir(s3, difflink)
    difflink = f"{furl}redir/{redirkey}"
    return f"{ref} ({catlink}) has changed: {difflink}"


def check_records(sess: requests.Session, s3, sns, furl: str):
    with ThreadPoolExecutor(max_workers=5) as executor:
        jobs: List[Future[CheckRecordResult]] = []

        records, etag = get_monitored_records(s3)
        LOGGER.debug(f"monitoring {len(records)} records")
        for item in records:
            jobs.append(executor.submit(check_record, sess, item))

        res = [job.result() for job in jobs]

    records = [newrecord for newrecord, _diff in res]
    put_monitored_records(s3, etag, records)

    mismatched = [
        (newrecord, alert_for_record(s3, furl, newrecord, diff[0], diff[1]))
        for newrecord, diff in res
        if diff is not None
    ]
    LOGGER.debug(
        f"found {len(records)} mismatched records",
        extra={"mismatched": [r["citableReference"] for r, _ in mismatched]},
    )
    for r, msg in mismatched:
        ref = r["citableReference"]
        publish_change(sns, f"Change in {ref}", msg)
