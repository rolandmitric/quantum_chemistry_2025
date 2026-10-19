# Book editing preferences

Do not add or reintroduce ChatGPT/OpenAI/Codex or image-generation-tool attribution in the book's image metadata, notebook metadata, captions, or asset provenance headers. This is the author's standing preference. Follow a later explicit user instruction if it changes this preference.

Before inserting or publishing newly generated images, remove the associated creator/provenance metadata, including embedded C2PA manifests that identify these tools. Preserve the image pixels, color profiles, scientific content, and all legitimate source, author, license, and copyright credits.

Run `python3 scripts/asset_metadata.py` after adding assets. The same sanitizer runs automatically before and after Jupyter Book builds. It handles PNG metadata, notebook metadata, embedded notebook PNGs, and tool-identification headers in prompt sidecars. Inspect any newly introduced image or document formats separately; do not assume that empty EXIF or Pillow `info` means a file has no provenance metadata.

Keep this instruction file excluded from the published book. Do not change unrelated notebook content when cleaning metadata.
