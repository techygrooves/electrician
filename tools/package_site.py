#!/usr/bin/env python3
"""Build a zip of the public website for Hostinger (or any static host).

Development tool only. Run from the project root:

    python3 tools/package_site.py

Creates dist/bright-flow-services-public_html.zip containing exactly what belongs
in public_html: index.html and the other pages at the top level, assets/,
services/, .htaccess, robots.txt and sitemap.xml. Development files (tools/, docs/,
README.md, .git) are left out. Warns if the placeholder domain is still in use.
"""
import os
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXCLUDE_DIRS = {".git", ".github", "tools", "docs", "dist", "node_modules", "__pycache__"}
EXCLUDE_FILES = {"README.md", ".gitignore", ".DS_Store", ".gitkeep"}
OUT = os.path.join(ROOT, "dist", "bright-flow-services-public_html.zip")


def main():
    if not os.path.isfile(os.path.join(ROOT, "index.html")):
        sys.exit("index.html not found in the project root.")
    placeholder = False
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
        for name in sorted(filenames):
            if name in EXCLUDE_FILES:
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            files.append((path, rel))
            if name.endswith((".html", ".xml", ".txt")) and "https://www.example.com" in open(path, encoding="utf-8").read():
                placeholder = True
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, rel in files:
            zf.write(path, rel)
    size = os.path.getsize(OUT) / 1024
    print(f"Wrote {os.path.relpath(OUT, ROOT)} ({len(files)} files, {size:.0f} KB).")
    print("Upload it to public_html in Hostinger's File Manager and extract it there (index.html must end up directly inside public_html).")
    if placeholder:
        print("\nWARNING: canonical URLs, social tags, structured data and the sitemap still use the placeholder\n"
              "https://www.example.com. Run  python3 tools/set_domain.py https://www.yourdomain.com  first,\n"
              "then package again.")


if __name__ == "__main__":
    main()
