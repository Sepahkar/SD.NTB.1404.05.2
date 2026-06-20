"""Inject shared student-panel shell assets into frontend HTML at serve time."""

from __future__ import annotations

import re

from core.frontend_registry import FRONTEND_PAGES, FrontendPage

STUDENT_PANEL_BODY_CLASS = "student-panel"

SHARED_STYLESHEETS = (
    "/static/amoozeshyar/yekan-bakh.css",
    "/static/amoozeshyar/student-panel.css",
)

SHARED_SCRIPTS = (
    "/static/amoozeshyar/api-client.js",
    "/static/amoozeshyar/utils.js",
    "/static/amoozeshyar/nav.js",
    "/static/amoozeshyar/notifications.js",
    "/static/amoozeshyar/auth.js",
)

_BODY_TAG_RE = re.compile(r"<body([^>]*)>", re.IGNORECASE)
_CLASS_ATTR_RE = re.compile(r"""class=(["'])(.*?)\1""", re.IGNORECASE)


def enrich_student_panel_html(html: str, page: FrontendPage) -> str:
    """Ensure authenticated frontend pages load the universal shell assets."""
    if not page.requires_auth:
        return html

    html = _ensure_body_class(html, STUDENT_PANEL_BODY_CLASS)
    html = _inject_stylesheets(html, SHARED_STYLESHEETS)
    html = _inject_scripts(html, SHARED_SCRIPTS)
    return html


def _ensure_body_class(html: str, class_name: str) -> str:
    match = _BODY_TAG_RE.search(html)
    if not match:
        return html

    attrs = match.group(1)
    class_match = _CLASS_ATTR_RE.search(attrs)
    if class_match:
        quote = class_match.group(1)
        classes = class_match.group(2).split()
        if class_name not in classes:
            classes.append(class_name)
            new_class = f'class={quote}{" ".join(classes)}{quote}'
            attrs = attrs[: class_match.start()] + new_class + attrs[class_match.end() :]
    else:
        attrs = f'{attrs} class="{class_name}"'

    return html[: match.start()] + f"<body{attrs}>" + html[match.end() :]


def _inject_stylesheets(html: str, stylesheets: tuple[str, ...]) -> str:
    insert_lines = []
    for href in stylesheets:
        if href not in html:
            insert_lines.append(f'    <link rel="stylesheet" href="{href}">')

    if not insert_lines:
        return html

    block = "\n".join(insert_lines) + "\n"
    if "</head>" in html:
        return html.replace("</head>", block + "</head>", 1)
    return block + html


def _inject_scripts(html: str, scripts: tuple[str, ...]) -> str:
    html_out = html
    for script in scripts:
        if script in html_out:
            continue

        tag = f'<script src="{script}"></script>\n'
        insert_pos = _script_insert_index(html_out, script, scripts)
        if insert_pos is None:
            html_out = html_out.replace("</body>", tag + "</body>", 1)
        else:
            html_out = html_out[:insert_pos] + tag + html_out[insert_pos:]
    return html_out


def _script_insert_index(html: str, script: str, scripts: tuple[str, ...]) -> int | None:
    script_idx = scripts.index(script)
    for later_script in scripts[script_idx + 1 :]:
        marker = f'<script src="{later_script}"></script>'
        pos = html.find(marker)
        if pos != -1:
            return pos
    return None


def enrich_frontend_html(html: str, slug: str) -> str:
    page = FRONTEND_PAGES.get(slug)
    if page is None:
        return html
    return enrich_student_panel_html(html, page)
