#!/usr/bin/env python3
"""Build the Compass section from Obsidian Markdown.

Publishing contract:
- Source: compass/**/*.md (folder names do not matter)
- Publish only notes with type: compass and status: published
- role: main => appears as a card in Compass Notes
- role: child => gets a web article and can be opened through wikilinks, but does not appear as a top-level card
- id is a stable identity; order controls display order
- modules are stored as M01..M10 codes and mapped to labels on the website
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import mistune
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "compass"
TEMPLATE = ROOT / "website-src" / "index.template.html"
OUTPUT = ROOT / "website-preview" / "index.html"

MODULE_LABELS = {
    "M01": "M01 身心管理",
    "M02": "M02 三观构建",
    "M03": "M03 学习能力",
    "M04": "M04 认知体系",
    "M05": "M05 技术赋能",
    "M06": "M06 职业发展",
    "M07": "M07 创业投资",
    "M08": "M08 想象力与审美",
    "M09": "M09 人际影响",
    "M10": "M10 儿童教育",
}
VALID_INPUT_TYPES = {"书籍", "课程", "文章", "论文", "讲座", "感悟", "其他"}


def split_frontmatter(text: str):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    raw = text[4:end]
    body = text[end + 4 :].lstrip("\r\n")
    data = yaml.safe_load(raw) or {}
    return data if isinstance(data, dict) else {}, body


def plain_heading(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"==(.+?)==", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def first_heading(body: str) -> str | None:
    m = re.search(r"(?m)^#\s+(.+?)\s*$", body)
    return plain_heading(m.group(1)) if m else None


def normalize_modules(value):
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    out = []
    for item in value:
        code = str(item).strip().split()[0]
        if code in MODULE_LABELS and code not in out:
            out.append(code)
    return out


def load_notes():
    notes = []
    if not SOURCE_DIR.exists():
        return notes
    for path in sorted(SOURCE_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body = split_frontmatter(text)
        if str(meta.get("type", "")).strip().lower() != "compass":
            continue
        if str(meta.get("status", "")).strip().lower() != "published":
            continue
        note_id = str(meta.get("id", "")).strip()
        if not note_id:
            print(f"SKIP {path}: published compass note has no id")
            continue
        title = str(meta.get("title") or first_heading(body) or path.stem).strip()
        input_type = str(meta.get("input_type") or "其他").strip()
        if input_type not in VALID_INPUT_TYPES:
            input_type = "其他"
        modules = normalize_modules(meta.get("modules"))
        try:
            order = int(meta.get("order", 999999))
        except Exception:
            order = 999999
        notes.append({
            "id": note_id,
            "title": title,
            "input_type": input_type,
            "modules": modules,
            "role": str(meta.get("role") or "main").strip().lower(),
            "parent": str(meta.get("parent") or "").strip(),
            "order": order,
            "date": str(meta.get("date") or "").strip(),
            "summary": str(meta.get("summary") or "").strip(),
            "source_title": str(meta.get("source_title") or "").strip(),
            "source_author": str(meta.get("source_author") or "").strip(),
            "body": body,
            "stem": path.stem,
            "path": path,
        })
    return notes


def replace_wikilinks(body: str, target_map: dict[str, str]) -> str:
    pattern = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")

    def repl(m):
        target = m.group(1).strip()
        anchor = (m.group(2) or "").strip()
        label = (m.group(3) or "").strip() or target
        if anchor and not m.group(3):
            label = f"{target} · {anchor}"
        note_id = target_map.get(target)
        safe_label = html.escape(label)
        if note_id:
            return f'<a href="#compass-note-{html.escape(note_id, quote=True)}" data-compass-id="{html.escape(note_id, quote=True)}">{safe_label}</a>'
        return f'<span class="wiki">{safe_label}</span>'

    return pattern.sub(repl, body)


def render_markdown(body: str, target_map: dict[str, str]):
    body = replace_wikilinks(body, target_map)
    body = re.sub(r"==(.+?)==", r"<mark>\1</mark>", body)
    renderer = mistune.HTMLRenderer(escape=False)
    md = mistune.create_markdown(
        renderer=renderer,
        plugins=["strikethrough", "table", "task_lists", "url"],
    )
    rendered = md(body)
    toc = []
    counter = 0

    def heading_repl(m):
        nonlocal counter
        level, inner = m.group(1), m.group(2)
        counter += 1
        sec_id = f"ca-sec-{counter}"
        toc.append({"id": sec_id, "text": plain_heading(inner)})
        return f'<h{level} id="{sec_id}">{inner}</h{level}>'

    rendered = re.sub(r"<h([1-4])>(.*?)</h\1>", heading_repl, rendered, flags=re.S)
    return rendered, toc


def card_html(note):
    labels = [MODULE_LABELS[m] for m in note["modules"]]
    tags = "".join(f"<span>{html.escape(x)}</span>" for x in labels)
    meta_right = html.escape(note["date"] or "持续更新")
    summary = html.escape(note["summary"] or "这篇罗盘笔记已经发布，点击阅读完整内容。")
    return (
        f'<article class="compass-note" data-note="{html.escape(note["id"], quote=True)}" '
        f'data-type="{html.escape(note["input_type"], quote=True)}" '
        f'data-modules="{html.escape(" ".join(note["modules"]), quote=True)}">\n'
        f'<div class="note-meta"><span class="note-type">{html.escape(note["input_type"])}</span><span>{meta_right}</span></div>\n'
        f'<h3>{html.escape(note["title"])}</h3>\n'
        f'<p>{summary}</p>\n'
        f'<div class="module-tags">{tags}</div>\n'
        f'<span class="read-note">阅读完整文章 →</span>\n'
        f'</article>'
    )


def build():
    notes = load_notes()
    target_map = {}
    for n in notes:
        target_map[n["id"]] = n["id"]
        target_map[n["stem"]] = n["id"]
        target_map[n["title"]] = n["id"]

    data = {}
    for note in notes:
        rendered, toc = render_markdown(note["body"], target_map)
        data[note["id"]] = {
            "id": note["id"],
            "title": note["title"],
            "type": note["input_type"],
            "summary": note["summary"],
            "modules": [MODULE_LABELS[m] for m in note["modules"]],
            "html": rendered,
            "toc": toc,
            "role": note["role"],
            "parent": note["parent"],
        }

    cards = [n for n in notes if n["role"] != "child"]
    cards.sort(key=lambda n: (n["order"], n["date"], n["id"]))
    cards_markup = "\n".join(card_html(n) for n in cards)

    template = TEMPLATE.read_text(encoding="utf-8")
    template = re.sub(
        r"<!-- COMPASS_CARDS_START -->.*?<!-- COMPASS_CARDS_END -->",
        "<!-- COMPASS_CARDS_START -->\n" + cards_markup + "\n<!-- COMPASS_CARDS_END -->",
        template,
        flags=re.S,
    )
    note_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    template = template.replace("/* COMPASS_NOTE_DATA */{}", note_json)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(template, encoding="utf-8")
    print(f"Built {OUTPUT.relative_to(ROOT)}: {len(cards)} main cards, {len(notes)} published articles")


if __name__ == "__main__":
    build()
