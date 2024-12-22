import json
import os

STORAGE_BUCKET = os.getenv("STORAGE_BUCKET")
RECORDS_KEY = "monitored_records.json"

if not STORAGE_BUCKET:
    raise Exception("Could not retrieve STORAGE_BUCKET")


def get_monitored_records(s3) -> tuple[list[object], str]:
    resp = s3.get_object(
        Bucket=STORAGE_BUCKET,
        Key=RECORDS_KEY,
    )
    body = json.loads(resp["Body"].read())
    return (body, str(resp["ETag"]))


def put_monitored_records(s3, old_etag: str, new: list[object]):
    s3.put_object(
        Body=json.dumps(new).encode("utf-8"),
        Bucket=STORAGE_BUCKET,
        Key=RECORDS_KEY,
        ContentType="application/json; charset=utf-8",
        IfMatch=old_etag,
    )
