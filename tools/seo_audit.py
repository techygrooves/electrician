#!/usr/bin/env python3
"""SEO audit for the Bright Flow Services static site.

Development tool only; the published website does not need it.
Run from the project root:   python3 tools/seo_audit.py
Exit code is 1 when errors are found, so it can be used as a pre-publish check.

Checks every .html file for:
  titles and meta descriptions (missing, duplicate, length), canonical URLs,
  robots directives, exactly one <h1>, skipped heading levels, broken internal
  links and #anchors, <img> alt attributes, Open Graph / Twitter metadata,
  JSON-LD syntax and basic required properties, and sitemap.xml / robots.txt
  consistency with the pages that are actually indexable.
"""
import json
import os
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TITLE_MAX, DESC_MIN, DESC_MAX = 65, 70, 160
SKIP_DIRS = {".git", "tools", "node_modules"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self._in_title = False
        self.meta = {}
        self.links = []          # (tag, attr, value)
        self.ids = set()
        self.headings = []       # (level, text)
        self._heading = None
        self.imgs = []           # attrs dicts
        self.jsonld = []
        self._in_ld = False
        self._ld_buf = []
        self.canonical = None
        self.depth_hidden = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "title":
            self._in_title = True
            self.title = ""
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key.lower()] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True
            self._ld_buf = []
        elif tag == "img":
            self.imgs.append(a)
        if re.fullmatch(r"h[1-6]", tag):
            self._heading = [int(tag[1]), ""]
        if tag == "link":
            if a.get("rel") in ("icon", "apple-touch-icon", "stylesheet", "manifest") and "href" in a:
                self.links.append((tag, "href", a["href"]))
        else:
            for attr in ("href", "src"):
                if attr in a:
                    self.links.append((tag, attr, a[attr]))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_ld:
            self._in_ld = False
            self.jsonld.append("".join(self._ld_buf))
        elif self._heading and tag == "h%d" % self._heading[0]:
            self.headings.append((self._heading[0], " ".join(self._heading[1].split())))
            self._heading = None

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ld:
            self._ld_buf.append(data)
        if self._heading:
            self._heading[1] += data


def html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in sorted(filenames):
            if f.endswith(".html"):
                yield os.path.relpath(os.path.join(dirpath, f), ROOT).replace(os.sep, "/")


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def public_url(site, rel):
    return site + "/" if rel == "index.html" else f"{site}/{rel}"


def check_ld(node, rel, report, path="$"):
    if isinstance(node, list):
        for i, n in enumerate(node):
            check_ld(n, rel, report, f"{path}[{i}]")
        return
    if not isinstance(node, dict):
        return
    if "@graph" in node:
        check_ld(node["@graph"], rel, report, path + ".@graph")
    t = node.get("@type")
    types = t if isinstance(t, list) else [t]
    if "BreadcrumbList" in types:
        items = node.get("itemListElement") or []
        for i, it in enumerate(items, 1):
            if it.get("position") != i or not it.get("name") or not it.get("item"):
                report("error", rel, f"BreadcrumbList item {i} is missing position/name/item")
    if "Service" in types:
        for k in ("name", "provider"):
            if not node.get(k):
                report("error", rel, f"Service is missing '{k}'")
    if "FAQPage" in types:
        for q in node.get("mainEntity", []):
            if not q.get("name") or not (q.get("acceptedAnswer") or {}).get("text"):
                report("error", rel, "FAQPage question without name or answer text")
    if any(x in types for x in ("Electrician", "LocalBusiness", "Organization")) and "name" in node:
        if not node.get("url"):
            report("warn", rel, f"{types} entity has no url")
    for k, v in node.items():
        if isinstance(v, (dict, list)):
            check_ld(v, rel, report, f"{path}.{k}")


def main():
    findings = defaultdict(list)
    counts = {"error": 0, "warn": 0}

    def report(level, page, msg):
        counts[level] += 1
        findings[page].append((level, msg))

    pages = {}
    for rel in html_files():
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            raw = fh.read()
        p = Page()
        p.feed(strip_comments(raw))
        pages[rel] = p

    # Site URL comes from the homepage canonical.
    home = pages.get("index.html")
    site = (home.canonical or "").rstrip("/") if home else ""
    if not site:
        report("error", "index.html", "homepage has no canonical URL; cannot determine the site URL")

    titles, descs = defaultdict(list), defaultdict(list)
    indexable = set()

    for rel, p in pages.items():
        robots = p.meta.get("robots", "index, follow").lower()
        noindex = "noindex" in robots
        if not noindex:
            indexable.add(rel)

        # Titles & descriptions
        title = (p.title or "").strip()
        if not title:
            report("error", rel, "missing <title>")
        else:
            titles[title].append(rel)
            if len(title) > TITLE_MAX:
                report("warn", rel, f"title is {len(title)} characters (over {TITLE_MAX} may be truncated)")
        desc = p.meta.get("description", "").strip()
        if not desc:
            report("error", rel, "missing meta description")
        else:
            descs[desc].append(rel)
            if not DESC_MIN <= len(desc) <= DESC_MAX:
                report("warn", rel, f"meta description is {len(desc)} characters (aim for {DESC_MIN}-{DESC_MAX})")

        # Canonical
        if not noindex:
            expected = public_url(site, rel)
            if not p.canonical:
                report("error", rel, "missing canonical")
            elif p.canonical != expected:
                report("error", rel, f"canonical {p.canonical} does not match {expected}")

        # Headings
        h1s = [h for h in p.headings if h[0] == 1]
        if len(h1s) != 1:
            report("error", rel, f"{len(h1s)} <h1> elements (expected exactly 1)")
        prev = 0
        for level, text in p.headings:
            if prev and level > prev + 1:
                report("error", rel, f"heading level skips from h{prev} to h{level} at \"{text[:50]}\"")
            prev = level
        if p.headings and p.headings[0][0] != 1:
            report("error", rel, f"first heading is h{p.headings[0][0]}, not h1")

        # Social metadata
        for key in ("og:title", "og:description", "og:url", "og:type", "og:image", "twitter:card"):
            if not p.meta.get(key):
                report("warn" if noindex else "error", rel, f"missing {key}")
        if p.meta.get("og:image") and not p.meta["og:image"].startswith("http"):
            report("error", rel, "og:image must be an absolute URL")

        # Images
        for img in p.imgs:
            if "alt" not in img:
                report("error", rel, f"<img src=\"{img.get('src')}\"> has no alt attribute")

        # Links
        base = os.path.dirname(rel)
        for tag, attr, value in p.links:
            if re.match(r"^(https?:|mailto:|tel:|data:|javascript:)", value) or value == "#":
                continue
            url = urlparse(value)
            if rel == "404.html" and url.path.startswith("/"):
                target = url.path.lstrip("/") or "index.html"
            elif url.path.startswith("/"):
                target = url.path.lstrip("/") or "index.html"
            elif url.path:
                target = os.path.normpath(os.path.join(base, unquote(url.path))).replace(os.sep, "/")
            else:
                target = rel
            if "/photos/" in target:  # optional photography slots
                continue
            if not os.path.exists(os.path.join(ROOT, target)):
                report("error", rel, f"broken link: {value}")
            elif url.fragment and target.endswith(".html"):
                tp = pages.get(target)
                if tp and url.fragment not in tp.ids:
                    report("error", rel, f"link to missing anchor: {value}")

        # Structured data
        for block in p.jsonld:
            try:
                data = json.loads(block)
            except json.JSONDecodeError as exc:
                report("error", rel, f"invalid JSON-LD: {exc}")
                continue
            check_ld(data, rel, report)

    for title, rels in titles.items():
        if len(rels) > 1:
            for r in rels:
                report("error", r, f"duplicate title shared with {', '.join(x for x in rels if x != r)}")
    for desc, rels in descs.items():
        if len(rels) > 1:
            for r in rels:
                report("error", r, f"duplicate meta description shared with {', '.join(x for x in rels if x != r)}")

    # Sitemap & robots
    sm_path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(sm_path):
        report("error", "sitemap.xml", "missing")
    else:
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [e.text.strip() for e in ET.parse(sm_path).getroot().findall("s:url/s:loc", ns)]
        listed = set()
        for loc in locs:
            if not loc.startswith(site + "/"):
                report("error", "sitemap.xml", f"URL outside the site: {loc}")
                continue
            path = loc[len(site) + 1:] or "index.html"
            listed.add(path)
            if path not in pages:
                report("error", "sitemap.xml", f"lists a page that does not exist: {loc}")
            elif path not in indexable:
                report("error", "sitemap.xml", f"lists a noindex page: {loc}")
        for rel in sorted(indexable - listed):
            report("error", "sitemap.xml", f"indexable page missing from sitemap: {rel}")
    rb_path = os.path.join(ROOT, "robots.txt")
    if not os.path.exists(rb_path):
        report("error", "robots.txt", "missing")
    else:
        rb = open(rb_path, encoding="utf-8").read()
        m = re.search(r"^Sitemap:\s*(\S+)", rb, flags=re.M | re.I)
        if not m:
            report("error", "robots.txt", "no Sitemap: line")
        elif m.group(1) != site + "/sitemap.xml":
            report("error", "robots.txt", f"Sitemap URL {m.group(1)} does not match {site}/sitemap.xml")
        if re.search(r"^Disallow:\s*/\s*$", rb, flags=re.M):
            report("error", "robots.txt", "Disallow: / blocks the whole site")

    # Report
    print(f"SEO audit of {len(pages)} HTML pages ({len(indexable)} indexable), site URL: {site or '?'}\n")
    for page in sorted(findings):
        print(page)
        for level, msg in findings[page]:
            print(f"  {level.upper():5} {msg}")
    noindexed = sorted(set(pages) - indexable)
    print(f"\nIntentionally noindex: {', '.join(noindexed) or 'none'}")
    print(f"Errors: {counts['error']}   Warnings: {counts['warn']}")
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
