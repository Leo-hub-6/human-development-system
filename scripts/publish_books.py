#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "罗盘笔记" / "书籍阅读"
OUTPUT = ROOT / "published-content" / "罗盘笔记" / "书籍阅读"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

def get_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    return text[4:end] if end >= 0 else ""

def is_published(text: str) -> bool:
    fm = get_frontmatter(text)
    m = re.search(r"(?mi)^status\s*:\s*['\"]?([^\n#'\"]+)", fm)
    return bool(m and m.group(1).strip().lower() == "published")

def referenced_assets(text: str) -> set[str]:
    refs = set()
    for m in re.finditer(r"!\[\[([^\]|#]+)", text):
        refs.add(m.group(1).strip())
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
        raw = m.group(1).strip().strip("<>")
        raw = raw.split(" \"", 1)[0].split(" '", 1)[0]
        refs.add(unquote(raw))
    return {r for r in refs if Path(r).suffix.lower() in IMAGE_EXTS}

def resolve_asset(note_path: Path, ref: str) -> Path | None:
    ref = ref.replace("\\", "/")
    direct = (note_path.parent / ref).resolve()
    try:
        direct.relative_to(SOURCE.resolve())
        if direct.is_file():
            return direct
    except ValueError:
        pass
    matches = list(SOURCE.rglob(Path(ref).name))
    return matches[0] if len(matches) == 1 else None

def main():
    if not SOURCE.exists():
        raise SystemExit(f"Source folder not found: {SOURCE}")

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    note_count = 0
    assets = set()

    for src in sorted(SOURCE.rglob("*.md")):
        text = src.read_text(encoding="utf-8")
        if not is_published(text):
            continue
        rel = src.relative_to(SOURCE)
        dst = OUTPUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        note_count += 1

        for ref in referenced_assets(text):
            asset = resolve_asset(src, ref)
            if asset:
                assets.add(asset)

    for asset in sorted(assets):
        rel = asset.relative_to(SOURCE)
        dst = OUTPUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(asset, dst)

    print(f"Published {note_count} note(s) and {len(assets)} referenced asset(s).")
    print(f"Output: {OUTPUT}")

if __name__ == "__main__":
    main()
