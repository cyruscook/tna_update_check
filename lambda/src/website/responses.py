import json
from base64 import b64encode
from html import escape
from typing import Any

from tna.records import get_link_by_id

RESPONSE_404 = """
<!DOCTYPE html>
<html>
    <head>
        <title>404 Not Found</title>
    </head>
    <body>
        <h1>404 Not Found</h1>
    </body>
</html>
"""

RESPONSE_VIEW_START = """
<!DOCTYPE html>
<html>
    <head>
        <title>TNA Monitor</title>
    </head>
    <body>
        <h1>TNA Monitor - Monitored Records:</h1>
        <form action="/edit" method="post">
            <div class="records">
"""
RESPONSE_VIEW_ADD = """
                <input type="text" name="addition" placeholder="New record" />
                <input type="submit" name="action-add" value="Add Record" />
"""
RESPONSE_RECORD = """
                <a href=\"{link}\">{ref}</a>
                <input type="submit" name="action-remove-{id}" value="Remove Record" />
"""
RESPONSE_ETAG = """
                <input type="hidden" name="old-etag" value="{etag}" />
                <input type="hidden" name="old-records" value="{old_records}" />
"""
RESPONSE_FORM_END = """
            </div>
        </form>
"""
RESPONSE_SUCCESSFUL_EDIT = """
        <p>{succesful_edit}</p>
"""
RESPONSE_VIEW_END = """
        <style>
            .records {
                display: grid;
                grid-template-columns: max-content max-content;
                grid-column-gap: 3em;
            }
            .records > * {
                height: fit-content;
            }
            .records > *:first-child {
                margin-bottom: 2em;
            }
        </style>
    </body>
</html>
"""


def build_view_response(
    records: list[Any], etag: str, succesful_edit: str | None = None
) -> str:
    # First sort records
    records.sort(key=lambda record: record["citableReference"])

    # Etag to HTML
    etag = escape(etag)
    old_records = b64encode(json.dumps(records).encode(encoding="utf-8")).decode(
        encoding="utf-8"
    )
    etag_html = RESPONSE_ETAG.format(etag=etag, old_records=old_records)

    # Now map records into HTML
    def record_to_html(record: Any) -> str:
        id = escape(record["id"])
        link = escape(get_link_by_id(record["id"]))
        ref = escape(record["citableReference"])
        return RESPONSE_RECORD.format(id=id, link=link, ref=ref)

    records_html = map(record_to_html, records)

    out = RESPONSE_VIEW_START + RESPONSE_VIEW_ADD + "".join(records_html)
    out += etag_html + RESPONSE_FORM_END
    if succesful_edit:
        succesful_edit = escape(succesful_edit)
        out += RESPONSE_SUCCESSFUL_EDIT.format(succesful_edit=succesful_edit)
    out += RESPONSE_VIEW_END
    return out
