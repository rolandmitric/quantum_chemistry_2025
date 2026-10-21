#!/bin/zsh
set -eu
cd -- "$(dirname -- "$0")"
if [[ -x /opt/homebrew/bin/python3 ]]; then
    book_python=/opt/homebrew/bin/python3
else
    book_python=python3
fi
exec "$book_python" scripts/offline_book.py serve
