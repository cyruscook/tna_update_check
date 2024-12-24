import json
import uuid

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
    key = str(uuid.uuid4())
    body[key] = dest
    s3.put_object(
        Body=json.dumps(body).encode("utf-8"),
        Bucket=STORAGE_BUCKET,
        Key=REDIRS_KEY,
        ContentType="application/json; charset=utf-8",
        IfMatch=resp["ETag"],
    )
    return key
