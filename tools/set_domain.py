#!/usr/bin/env python3
"""Replace the placeholder domain with the real production domain.

Development tool only. Run from the project root once the domain is confirmed:

    python3 tools/set_domain.py https://www.yourdomain.com

It rewrites canonical URLs, Open Graph/Twitter URLs, JSON-LD, sitemap.xml,
robots.txt and the commented host rule in .htaccess. Run it once; afterwards
run tools/seo_audit.py to confirm everything is consistent.
"""
import os
import re
import sys

PLACEHOLDER = "https://www.example.com"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TARGETS = (".html", ".xml", ".txt")


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"https://[a-z0-9.-]+\.[a-z]{2,}", sys.argv[1].rstrip("/")):
        sys.exit("Usage: python3 tools/set_domain.py https://www.yourdomain.com")
    domain = sys.argv[1].rstrip("/")
    host = domain.split("://", 1)[1]
    changed = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in {".git", "tools"}]
        for name in filenames:
            if not name.endswith(TARGETS) and name != ".htaccess":
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            new = text.replace(PLACEHOLDER, domain)
            if name == ".htaccess":
                new = new.replace(r"www\.example\.com", re.escape(host)).replace("www.example.com", host)
            if new != text:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
                changed += 1
                print("updated", os.path.relpath(path, ROOT))
    print(f"{changed} files updated. Now run tools/seo_audit.py.")


if __name__ == "__main__":
    main()
