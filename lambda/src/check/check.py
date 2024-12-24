import requests
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from tna.records import get_record_by_id, get_link_by_id
from storage.monitored import get_monitored_records, put_monitored_records
from check.alert import publish_change
from storage.redirs import put_redir

JDIFF = "https://benjamine.github.io/jsondiffpatch/index.html?desc=diff&left={left}&right={right}"


def check_record(sess: requests.Session, record: object) -> tuple[object, tuple[str, str] | None]:
    id = record["id"]
    newr = get_record_by_id(sess, id)
    oldj = json.dumps(record, sort_keys=True)
    newj = json.dumps(newr, sort_keys=True)
    if oldj == newj:
        return (newr, None)
    return (newr, (oldj, newj))

def alert_for_record(s3, furl: str, record: object, oldj: str, newj: str) -> str:
    id = record["id"]
    ref = record["citableReference"]
    catlink = get_link_by_id(id)
    difflink = JDIFF.format(left=urllib.parse.quote(oldj), right=urllib.parse.quote(newj))
    redirkey = urllib.parse.quote(put_redir(s3, difflink), safe="")
    difflink = f"{furl}redir/{redirkey}"
    return f"{ref} ({catlink}) has changed: {difflink}"

def check_records(sess: requests.Session, s3, sns, furl: str):
    with ThreadPoolExecutor(max_workers=5) as executor:
        jobs = []

        records, etag = get_monitored_records(s3)
        for item in records:
            jobs.append(executor.submit(check_record, sess, item))

        res = [job.result() for job in jobs]
    
    records = [r for r, m in res]
    put_monitored_records(s3, etag, records)

    mismatched = [(r, alert_for_record(s3, furl, r, m[0], m[1])) for r, m in res if m is not None]
    for r, msg in mismatched:
        ref = r["citableReference"]
        publish_change(sns, f"Change in {ref}", msg)

