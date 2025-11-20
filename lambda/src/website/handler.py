import json
import logging
import os
import traceback
import urllib.parse
from base64 import b64decode
from html import escape
from typing import Any

from storage.monitored import get_monitored_records, put_monitored_records
from storage.redirs import get_redir
from tna.records import get_record_by_id, get_record_by_ref
from website.responses import RESPONSE_404, build_view_response

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ.get("LOGLEVEL", "INFO").upper())


def handle_web_request(sess, s3, request) -> object:
    path = request["rawPath"]
    try:
        method = request["requestContext"]["http"]["method"].lower()
        if (path == "/" or path == "") and method == "get":
            return handle_view(s3, request)
        elif path == "/edit" and method == "post":
            return handle_edit(sess, s3, request)
        elif path.startswith("/redir/") and method == "get":
            key = urllib.parse.unquote(path[len("/redir/") :])
            return handle_redir(s3, key)

        LOGGER.warning("Unknown request path", extra={"path": path, "method": method})
        return create_reponse(404, RESPONSE_404)
    except Exception as e:
        LOGGER.exception("Error handling web request")
        return create_reponse(
            500, escape(repr(e)) + "\n<pre>" + escape(traceback.format_exc()) + "</pre>"
        )


def handle_view(s3, request) -> object:
    edit_msg = None
    if (
        "queryStringParameters" in request
        and "edit_msg" in request["queryStringParameters"]
    ):
        edit_msg = request["queryStringParameters"]["edit_msg"]
    records, etag = get_monitored_records(s3)
    return create_reponse(200, build_view_response(records, etag, edit_msg))


def handle_edit(sess, s3, request) -> object:
    body = request["body"]
    if "isBase64Encoded" in request and request["isBase64Encoded"]:
        body = b64decode(body).decode("utf-8")
    body = urllib.parse.parse_qs(body)

    old_etag = body["old-etag"][0]
    records: list[Any] = json.loads(b64decode(body["old-records"][0]))

    edit_msg = None

    if "action-add" in body:
        # Adding a new record
        new_ref = str(body["addition"][0]).strip()
        LOGGER.info("Adding item %s", new_ref)
        if any(r["citableReference"] == new_ref for r in records):
            raise Exception("Already in records")

        new_record = get_record_by_ref(sess, new_ref)
        if any(r["id"] == new_record["id"] for r in records):
            raise Exception("Already in records")

        id = new_record["id"]
        # id/ref endpoints return different JSON
        # Need to refetch from id endpoint
        new_record = get_record_by_id(sess, id)
        ref = new_record["citableReference"]
        records.append(new_record)
        edit_msg = f"Successfully added record {ref}"
    else:
        # Removing a record - find which
        remove_action = next(k for k in body if k.startswith("action-remove-"))
        if not remove_action:
            raise Exception("No remove actions to process")

        rem_id = remove_action[len("action-remove-") :]
        LOGGER.info("Removing item %s", rem_id)

        record_to_remove = next(record for record in records if record["id"] == rem_id)
        if not record_to_remove:
            raise Exception("Cant find record")
        records.remove(record_to_remove)

        ref = record_to_remove["citableReference"]
        edit_msg = f"Successfully removed record {ref}"

    put_monitored_records(s3, old_etag, records)

    edit_msg = urllib.parse.quote(edit_msg, safe="")
    return create_reponse(303, "", redirect=f"/?edit_msg={edit_msg}")


def handle_redir(s3, key) -> object:
    redir = get_redir(s3, key)
    return create_reponse(308, "", redirect=redir)


def create_reponse(status: int, body: str, redirect: str | None = None) -> object:
    out = {
        "statusCode": status,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
        },
        "body": body,
        "cookies": [],
        "isBase64Encoded": False,
    }
    if redirect:
        out["headers"]["Location"] = redirect
    return out
