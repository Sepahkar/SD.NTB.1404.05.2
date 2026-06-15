import mimetypes
from pathlib import Path

from django.http import FileResponse, Http404, HttpResponse
from django.views import View

from core.frontend_registry import FRONTEND_PAGES, MIME_TYPES, get_page_directory, get_page_html_path


class LogoutPageView(View):
    """Clear Django session and run client-side token cleanup."""

    def get(self, request):
        request.session.flush()
        return HttpResponse(
            """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>خروج از سامانه</title>
  <link rel="stylesheet" href="/static/amoozeshyar/yekan-bakh.css">
</head>
<body>
  <p style="text-align:center;margin-top:2rem;">در حال خروج از سامانه...</p>
  <script src="/static/amoozeshyar/auth.js"></script>
  <script>logout();</script>
</body>
</html>""",
            content_type="text/html; charset=utf-8",
        )


class FrontendSiteView(View):
    """Serve frontend HTML pages and their static assets by slug."""

    slug: str | None = None

    def get(self, request, slug=None, asset_path=None):
        slug = self.slug or slug
        if not slug or slug not in FRONTEND_PAGES:
            raise Http404

        page_dir = get_page_directory(slug)
        if page_dir is None or not page_dir.is_dir():
            raise Http404

        if asset_path:
            return self._serve_asset(page_dir, asset_path)

        html_path = get_page_html_path(slug)
        if html_path is None:
            raise Http404

        return FileResponse(open(html_path, "rb"), content_type="text/html; charset=utf-8")

    def _serve_asset(self, page_dir: Path, asset_path: str) -> FileResponse:
        safe_path = Path(asset_path)
        if ".." in safe_path.parts or safe_path.is_absolute():
            raise Http404

        candidate = (page_dir / safe_path).resolve()
        page_root = page_dir.resolve()

        try:
            candidate.relative_to(page_root)
        except ValueError:
            raise Http404 from None

        if not candidate.is_file():
            raise Http404

        content_type = MIME_TYPES.get(candidate.suffix.lower())
        if not content_type:
            guessed, _ = mimetypes.guess_type(str(candidate))
            content_type = guessed or "application/octet-stream"

        return FileResponse(open(candidate, "rb"), content_type=content_type)
