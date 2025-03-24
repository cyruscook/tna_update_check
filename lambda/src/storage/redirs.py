import json
import uuid
import datetime

from storage.monitored import STORAGE_BUCKET

REDIRS_KEY = "redirs.json"


def get_redir(s3, key: str) -> str:
    resp = s3.get_object(
        Bucket=STORAGE_BUCKET,
        Key=REDIRS_KEY,
    )
    body = json.loads(resp["Body"].read())
    return body[key]


def put_redir(s3, dest: str) -> str:
    resp = s3.get_object(
        Bucket=STORAGE_BUCKET,
        Key=REDIRS_KEY,
    )
    body = json.loads(resp["Body"].read())

    datestr = datetime.datetime.now().strftime("%Y-%m-%d")
    uuidstr = str(uuid.uuid4())
    key = f"{datestr}/{uuidstr}"
    body[key] = dest

    bodystr = json.dumps(body, sort_keys=True).encode("utf-8")
    s3.put_object(
        Body=bodystr,
        Bucket=STORAGE_BUCKET,
        Key=REDIRS_KEY,
        ContentType="application/json; charset=utf-8",
        IfMatch=resp["ETag"],
    )
    return key
