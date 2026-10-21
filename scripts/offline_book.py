#!/usr/bin/env python3
"""Prepare an offline copy of the built book, or serve it without dependencies.

While online, after building the book:
    python3 scripts/offline_book.py prepare
In the lecture hall:
    python3 scripts/offline_book.py serve

The source notebooks and normal HTML build are never modified.
"""

import argparse
import base64
from functools import partial
import hashlib
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import threading
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
import webbrowser


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_build/html"
OUTPUT = ROOT / "_build/offline"
CACHE = ROOT / "_build/offline-downloads"
PACKAGES = {"mathjax": "3.2.2", "requirejs": "2.3.6", "font-awesome": "4.7.0"}
DIRAC_URL = "https://upload.wikimedia.org/wikipedia/commons/5/50/Paul_Dirac%2C_1933.jpg"


def download(url, destination):
    if destination.exists():
        return destination.read_bytes()
    print(f"Downloading {url}", flush=True)
    request = Request(url, headers={"User-Agent": "QuantumChemistryOfflineBook/1.0"})
    with urlopen(request, timeout=45) as response:
        data = response.read()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    temporary.write_bytes(data)
    temporary.replace(destination)
    return data


def install_package(name, version, vendor):
    metadata = json.loads(download(
        f"https://registry.npmjs.org/{name}/{version}",
        CACHE / f"{name}-{version}.json",
    ))
    data = download(metadata["dist"]["tarball"], CACHE / f"{name}-{version}.tgz")
    integrity = metadata["dist"].get("integrity")
    if integrity:
        algorithm, expected = integrity.split("-", 1)
        actual = base64.b64encode(hashlib.new(algorithm, data).digest()).decode()
        if actual != expected:
            raise ValueError(f"Checksum mismatch: {name}")
    elif hashlib.sha1(data).hexdigest() != metadata["dist"]["shasum"]:
        raise ValueError(f"Checksum mismatch: {name}")
    destination = vendor / name
    # Copy regular files only, preserving package licenses and font directories.
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive.getmembers():
            parts = PurePosixPath(member.name).parts
            if not member.isfile():
                continue
            if not parts or parts[0] != "package" or ".." in parts:
                raise ValueError(f"Unexpected archive path: {member.name}")
            target = destination.joinpath(*parts[1:])
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        keys = ("href",) if tag == "link" else ("src", "poster")
        for key in keys:
            if attrs.get(key):
                self.urls.append(attrs[key])


def check_resources():
    missing, external = [], []
    for page in OUTPUT.rglob("*.html"):
        # Theme templates and bundled library examples are not rendered book pages.
        if page.relative_to(OUTPUT).parts[0] == "_static":
            continue
        parser = Resources()
        parser.feed(page.read_text())
        for resource in parser.urls:
            url = urlsplit(resource)
            if url.scheme in {"http", "https"} or url.netloc:
                external.append((str(page.relative_to(OUTPUT)), resource))
            elif not url.scheme and url.path:
                target = (page.parent / unquote(url.path)).resolve()
                if not target.is_file():
                    missing.append((str(page.relative_to(OUTPUT)), resource))
    if missing:
        raise ValueError(f"Missing local resources: {missing}")
    online = [item for item in external if urlsplit(item[1]).hostname != "localhost"]
    if online:
        raise ValueError(f"Unbundled online resources: {online}")
    return external


def prepare():
    if not (SOURCE / "index.html").is_file():
        raise SystemExit("Build the book first; _build/html/index.html is missing.")
    CACHE.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ready = OUTPUT / "offline-ready.json"
    ready.unlink(missing_ok=True)
    shutil.copytree(SOURCE, OUTPUT, dirs_exist_ok=True)
    vendor = OUTPUT / "_static/offline-vendor"
    for name, version in PACKAGES.items():
        install_package(name, version, vendor)
    portrait = vendor / "images/Paul_Dirac_1933.jpg"
    portrait.parent.mkdir(parents=True, exist_ok=True)
    portrait.write_bytes(download(DIRAC_URL, CACHE / portrait.name))
    replacements = {
        "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js": "mathjax/es5/tex-mml-chtml.js",
        "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js": "requirejs/require.js",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css": "font-awesome/css/font-awesome.min.css",
        "https://maxcdn.bootstrapcdn.com/font-awesome/4.4.0/css/font-awesome.min.css": "font-awesome/css/font-awesome.min.css",
        DIRAC_URL: "images/Paul_Dirac_1933.jpg",
    }
    for page in OUTPUT.rglob("*.html"):
        html = page.read_text()
        for remote, local in replacements.items():
            relative = Path(os.path.relpath(vendor / local, page.parent)).as_posix()
            html = html.replace(remote, relative)
        page.write_text(html)
    existing_issues = check_resources()
    ready.write_text(json.dumps({
        "packages": PACKAGES,
        "source": str(SOURCE),
        "existing_missing_localhost_images": existing_issues,
        "limitations": "Binder/Thebe and Python-driven widgets need an online or local kernel.",
    }, indent=2) + "\n")
    print(f"Offline book ready: {OUTPUT}")
    for page, resource in existing_issues:
        print(f"Existing missing image in {page}: {resource}")
    print("Start with: python3 scripts/offline_book.py serve")


def serve(port, open_browser):
    if not (OUTPUT / "offline-ready.json").is_file():
        raise SystemExit("Prepare the offline copy while online: python3 scripts/offline_book.py prepare")
    handler = partial(SimpleHTTPRequestHandler, directory=str(OUTPUT))
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError:
        if port == 0:
            raise
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    url = f"http://127.0.0.1:{server.server_port}/index.html"
    print(f"Offline book: {url}", flush=True)
    print("Leave this window open during the lecture. Press Ctrl+C to stop.", flush=True)
    if open_browser:
        threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "serve", "check"))
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "check":
        for issue in check_resources():
            print("Existing missing image:", *issue)
        print("All other page resources are local and present.")
    else:
        serve(args.port, not args.no_browser)


if __name__ == "__main__":
    main()
