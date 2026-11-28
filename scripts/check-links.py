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
        self.has_article = False
        self.h1_count = 0
        self.canonical = []
        self.share_meta = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "article" and "next-article" in attributes.get("class", "").split():
            self.has_article = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "link" and attributes.get("rel") == "canonical":
            self.canonical.append(attributes.get("href", ""))
        if tag == "meta" and attributes.get("property", "").startswith("og:"):
            self.share_meta.setdefault(attributes["property"], []).append(attributes.get("content", ""))
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
        if file.name != "404.html":
            for key in ("og:title", "og:description", "og:url"):
                values = page.share_meta.get(key, [])
                if len(values) != 1 or not values[0].strip():
                    errors.append((file.relative_to(ROOT), key, "分享信息需要且只能有一个非空值"))
            if (len(page.canonical) != 1 or not page.canonical[0].strip()
                    or urlsplit(page.canonical[0]).scheme not in {"http", "https"}
                    or not urlsplit(page.canonical[0]).netloc
                    or page.share_meta.get("og:url") != page.canonical):
                errors.append((file.relative_to(ROOT), "canonical", "规范地址与分享地址不一致"))
        if page.has_article and page.h1_count != 1:
            errors.append((file.relative_to(ROOT), "h1", f"文章需要一个一级标题，实际为 {page.h1_count} 个"))
        for href in page.links:
            if not href.strip() or href.strip() == "#":
                errors.append((file.relative_to(ROOT), href, "空链接"))
                continue
            url = urlsplit(href)
            if url.scheme.lower() in {"file", "javascript"} or url.path.startswith("/Users/"):
                errors.append((file.relative_to(ROOT), href, "本机文件或不安全链接"))
                continue
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
