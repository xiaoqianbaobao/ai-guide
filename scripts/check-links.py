"""Check built internal links and static heading anchors under /ai-guide/."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1] / "dist"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag == "a" and "href" in attributes:
            self.links.append(attributes["href"])


def main():
    if not (ROOT / "index.html").is_file():
        raise SystemExit("请先执行 npm run build")
    pages = {}
    for file in ROOT.rglob("*.html"):
        page = Page()
        page.feed(file.read_text(encoding="utf-8"))
        pages[file.resolve()] = page
    errors = []
    count = 0
    for file, page in pages.items():
        for href in page.links:
            url = urlsplit(href)
            if url.scheme or url.netloc or href.startswith("//"):
                continue
            path = unquote(url.path)
            if path.startswith("/ai-guide/"):
                target = ROOT / path[len("/ai-guide/"):]
            elif path.startswith("/"):
                continue  # Paths outside this site may belong to the server's other apps.
            elif path:
                target = file.parent / path
            else:
                target = file
            if target.is_dir():
                target = target / "index.html"
            if not target.exists() and not target.suffix:
                target = target.with_suffix(".html")
            count += 1
            if not target.exists():
                errors.append((file.relative_to(ROOT), href, "目标不存在"))
            elif url.fragment and target.resolve() in pages and unquote(url.fragment) not in pages[target.resolve()].ids:
                errors.append((file.relative_to(ROOT), href, "静态锚点不存在"))
    for file, href, reason in errors:
        print(f"{file}: {href} — {reason}")
    print(f"检查 {len(pages)} 个页面、{count} 个站内链接，发现 {len(errors)} 个问题。")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
