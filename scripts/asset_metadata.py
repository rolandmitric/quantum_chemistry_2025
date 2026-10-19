"""Remove generator metadata from PNGs, notebooks, and prompt headers.

PNG image/color chunks and notebook scientific content are preserved. This
module does not process other image/document formats; inspect those separately.
Run with Python, or load as a local Sphinx extension to clean book assets.
"""

import argparse
import base64
import json
import os
from pathlib import Path
import re
import zlib


MARKERS = re.compile(r"chatgpt|openai|codex|image_gen|gpt-image", re.IGNORECASE)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_METADATA = {b"caBX", b"tEXt", b"zTXt", b"iTXt", b"eXIf"}
SKIP_DIRS = {
    ".git", ".hg", ".svn", "_build", "docs", ".venv", "venv", "env",
    ".cache", "__pycache__", ".ipynb_checkpoints", "node_modules",
}
REMOVED = object()


def _matches(value):
    if isinstance(value, bytes):
        # Also recognize ASCII names stored as UTF-16 in EXIF metadata.
        value = value.replace(b"\x00", b"").decode("utf-8", errors="ignore")
    return isinstance(value, str) and MARKERS.search(value) is not None


def _png_metadata(kind, payload):
    if kind == b"zTXt":
        keyword, rest = payload.split(b"\x00", 1)
        if not rest or rest[0] != 0:
            raise ValueError("Unsupported PNG text compression")
        return keyword + b"\n" + zlib.decompress(rest[1:])
    if kind == b"iTXt":
        keyword, rest = payload.split(b"\x00", 1)
        if len(rest) < 2:
            raise ValueError("Truncated PNG international text")
        flag, method = rest[:2]
        language, translated, text = rest[2:].split(b"\x00", 2)
        if flag == 1 and method == 0:
            text = zlib.decompress(text)
        elif flag != 0:
            raise ValueError("Unsupported PNG international text compression")
        return b"\n".join((keyword, language, translated, text))
    return payload


def clean_png(data):
    """Drop only matching metadata chunks, without decoding/re-encoding pixels."""
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("Invalid PNG signature")
    parts = [PNG_SIGNATURE]
    position = len(PNG_SIGNATURE)
    while position < len(data):
        length = int.from_bytes(data[position:position + 4], "big")
        end = position + length + 12
        if end > len(data):
            raise ValueError("Truncated PNG chunk")
        kind = data[position + 4:position + 8]
        payload = data[position + 8:end - 4]
        if kind not in PNG_METADATA or not _matches(_png_metadata(kind, payload)):
            parts.append(data[position:end])
        position = end
        if kind == b"IEND":
            parts.append(data[position:])
            return b"".join(parts)
    raise ValueError("PNG has no IEND chunk")


def _clean_metadata(value):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if not _matches(key):
                cleaned = _clean_metadata(item)
                if cleaned is not REMOVED:
                    result[key] = cleaned
        return result
    if isinstance(value, list):
        return [cleaned for item in value
                if (cleaned := _clean_metadata(item)) is not REMOVED]
    return REMOVED if _matches(value) else value


def _clean_mime(bundle):
    original = bundle.get("image/png")
    if original is None:
        return
    encoded = "".join(original) if isinstance(original, list) else original
    data = base64.b64decode(encoded)
    cleaned = clean_png(data)
    if cleaned != data:
        encoded = base64.b64encode(cleaned).decode("ascii")
        bundle["image/png"] = [encoded] if isinstance(original, list) else encoded


def clean_notebook(data):
    """Clean metadata and embedded PNGs, leaving cell sources/text untouched."""
    notebook = json.loads(data)
    before = json.dumps(notebook, ensure_ascii=False)
    objects = [notebook]
    for cell in notebook.get("cells", []):
        objects.append(cell)
        for bundle in cell.get("attachments", {}).values():
            _clean_mime(bundle)
        for output in cell.get("outputs", []):
            objects.append(output)
            _clean_mime(output.get("data", {}))
    for item in objects:
        if "metadata" in item:
            item["metadata"] = _clean_metadata(item["metadata"])
    if json.dumps(notebook, ensure_ascii=False) == before:
        return data
    return (json.dumps(notebook, ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def _clean_prompt(data):
    text = data.decode("utf-8")
    return "".join(
        line for line in text.splitlines(keepends=True)
        if not (re.match(r"\s*(?:Tool:|Generated using\b)", line, re.IGNORECASE)
                and _matches(line))
    ).encode("utf-8")


def sanitize_tree(root):
    """Clean supported assets beneath root; return changed relative paths."""
    root = Path(root)
    changed = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs
                         if name not in SKIP_DIRS and not name.startswith(".venv")
                         and not (Path(directory) / name).is_symlink())
        for name in sorted(files):
            path = Path(directory) / name
            if path.is_symlink():
                continue
            suffix = path.suffix.lower()
            cleaner = {".png": clean_png, ".ipynb": clean_notebook}.get(suffix)
            if suffix == ".txt" and "prompt" in name.lower():
                cleaner = _clean_prompt
            if cleaner is None:
                continue
            original = path.read_bytes()
            cleaned = cleaner(original)
            if cleaned != original:
                path.write_bytes(cleaned)
                changed.append(path.relative_to(root).as_posix())
    return changed


def _clean_build_tree(root):
    from sphinx.util import logging

    changed = sanitize_tree(root)
    if changed:
        logging.getLogger(__name__).info("Removed generator metadata from %d files", len(changed))


def _before_build(app):
    _clean_build_tree(app.srcdir)


def _after_build(app, exception):
    if exception is None:
        _clean_build_tree(app.outdir)


def setup(app):
    app.connect("builder-inited", _before_build)
    app.connect("build-finished", _after_build)
    return {"version": "1", "parallel_read_safe": True, "parallel_write_safe": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()
    for changed_path in sanitize_tree(args.root):
        print(changed_path)
