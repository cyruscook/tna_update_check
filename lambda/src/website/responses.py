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
            <div id="records">
"""
RESPONSE_VIEW_ADD = """
                <div id="record">
                    <input type="text" name="addition" placeholder="New record" />
                    <input type="submit" name="action-add" value="Add Record" />
                </div>
"""
RESPONSE_FORM_END = """
            </div>
        </form>
"""
RESPONSE_VIEW_END = """
        <style>
            #records {
                display: grid;
                grid-template-columns: max-content;
            }
            #record > input[type="submit"] {
                float: right;
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
    etag_html = f"""
    <input type="hidden" name="old-etag" value="{etag}" />
    <input type="hidden" name="old-records" value="{old_records}" />
    """

    # Now map records into HTML
    def record_to_html(record) -> str:
        id = escape(record["id"])
        link = escape(get_link_by_id(record["id"]))
        ref = escape(record["citableReference"])
        return f"""
        <div id="record">
            <a href=\"{link}\">{ref}</a>
            <input type="submit" name="action-remove-{id}" value="Remove Record" />
        </div>
        """

    records_html = map(record_to_html, records)

    out = RESPONSE_VIEW_START + RESPONSE_VIEW_ADD + "".join(records_html)
    out += etag_html + RESPONSE_FORM_END
    if succesful_edit:
        succesful_edit = escape(succesful_edit)
        out += f"<p>{succesful_edit}</p>"
    out += RESPONSE_VIEW_END
    return out
