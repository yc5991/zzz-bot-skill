# -*- coding: utf-8 -*-
"""构建 kb/：世界观 + 角色卡 + 剧情（已校正）+ SQLite FTS5 检索索引。

在项目根目录运行：
    python kb/tools/build_kb.py
"""
import glob
import json
import os
import re
import sqlite3
import sys
from collections import Counter, OrderedDict

import jieba

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WIKI = os.path.join(ROOT, "参考wiki")
if not os.path.exists(WIKI):
    WIKI = os.path.join(ROOT, "_work", "参考wiki")
WORK = os.path.join(ROOT, "_work", "bili-transcribe")
KB = os.path.join(ROOT, "rag")
GLOSSARY = json.load(open(os.path.join(ROOT, "_work", "rag", "glossary.json"), encoding="utf-8"))

CHARS = {c["canonical"]: c for c in GLOSSARY["characters"]}
TERMS = {t["canonical"]: t for t in GLOSSARY["terms"]}
FACTIONS = {f["canonical"]: f for f in GLOSSARY["factions"]}

# 单字名里只认这几个不会被普通词淹没的
SAFE_SINGLE = {"哲", "铃"}

os.makedirs(os.path.join(KB, "world"), exist_ok=True)
os.makedirs(os.path.join(KB, "characters"), exist_ok=True)
os.makedirs(os.path.join(KB, "plot"), exist_ok=True)
os.makedirs(os.path.join(KB, "index"), exist_ok=True)
os.makedirs(os.path.join(KB, "tools"), exist_ok=True)


def read(path):
    return open(path, encoding="utf-8").read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def fmt_dur(sec):
    h, r = divmod(int(sec), 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# ── 1. 世界观 ────────────────────────────────────────────────
world_raw = read(os.path.join(WIKI, "世界观.md"))
lines = []
for ln in world_raw.splitlines():
    m = re.match(r"^(=+)\s*(.*?)\s*=+\s*$", ln)
    if m:
        level = max(2, len(m.group(1)))
        lines.append("#" * level + " " + m.group(2))
        continue
    if ln.startswith("# "):
        lines.append("# 世界观（绝区零）")
    elif ln.startswith("::"):
        s = ln.lstrip(":").strip("'")
        if s:
            lines.append("> " + s)
    elif ln.startswith("* "):
        lines.append("- " + ln[2:])
    else:
        lines.append(ln)
write(os.path.join(KB, "world", "世界观.md"), "\n".join(lines).replace("\n\n\n", "\n\n"))

# 时间线
# 时间线为人工维护的游戏内时间线，构建时不要用 wiki 的版本历史覆盖
# （旧逻辑：read(WIKI/版本历史.md) -> world/时间线.md，已移除）

# 术语表
rows = ["# 术语表", "", "| 规范名 | 类别 | 别名 | 拼音 |", "|---|---|---|---|"]
for c in GLOSSARY["characters"]:
    rows.append(f"| {c['canonical']} | 角色 | {'、'.join(c['aliases']) or '—'} | {c['pinyin']} |")
for f in GLOSSARY["factions"]:
    rows.append(f"| {f['canonical']} | 势力 | — | {f['pinyin']} |")
for t in GLOSSARY["terms"]:
    rows.append(f"| {t['canonical']} | 设定 | — | {t['pinyin']} |")
write(os.path.join(KB, "world", "术语表.md"), "\n".join(rows) + "\n")

# 势力清单由 _work/rag/11_factions.py 按实际目录生成，构建时不覆盖

# ── 2. 角色卡（保留档案/情报/台词/剧情，去掉技能数值）─────────
KEEP_SECTIONS = {"官方档案", "详细情报（含信赖解锁）", "天赋（含背景台词）", "剧情相关", "哲与铃的合作备注"}
char_index = {}
for path in sorted(glob.glob(os.path.join(WIKI, "角色", "*.md"))):
    name = os.path.splitext(os.path.basename(path))[0]
    text = read(path)
    parts = re.split(r"\n(?=## )", text)
    head = parts[0]
    kept = [head]
    for sec in parts[1:]:
        title = sec.split("\n", 1)[0].lstrip("# ").strip()
        if title in KEEP_SECTIONS:
            kept.append(sec)
    body = "\n".join(kept).strip() + "\n"
    # 头部的“别名”行补一下
    meta = CHARS.get(name, {})
    extra = []
    if meta.get("aliases"):
        extra.append(f"- 别名：{'、'.join(meta['aliases'])}")
    if meta.get("english"):
        extra.append(f"- 英文名：{meta['english']}")
    if extra:
        body += "\n## 索引字段\n\n" + "\n".join(extra) + "\n"
    write(os.path.join(KB, "characters", f"{name}.md"), body)
    char_index[name] = {"file": f"characters/{name}.md", "faction": meta.get("faction", "")}
write(os.path.join(KB, "characters", "_index.json"),
      json.dumps(char_index, ensure_ascii=False, indent=1))

# ── 3. 剧情（校正稿 + 对照卡）────────────────────────────────
pages = json.load(open(os.path.join(WORK, "episodes.json"), encoding="utf-8"))["pages"]
fixed_seg_dir = os.path.join(WORK, "segments_fixed")


def season_of(part):
    m = re.match(r"^(第[一二三四五六七八九十]+季(?:尾音)?)", part)
    return m.group(1) if m else "其他"


def entities(text):
    found_c, found_t = Counter(), Counter()
    for name in CHARS:
        if len(name) >= 2 or name in SAFE_SINGLE:
            n = text.count(name)
            if n:
                found_c[name] = n
    for name in list(TERMS) + list(FACTIONS):
        n = text.count(name)
        if n:
            found_t[name] = n
    return found_c, found_t


plot_index = []
plot_chunks = []
for pg in pages:
    n = pg["page"]
    season = season_of(pg["part"])
    seg_path = os.path.join(fixed_seg_dir, f"P{n:03}.json")
    segs = json.load(open(seg_path, encoding="utf-8")).get("segments") or []
    text = "".join((s.get("text") or "") for s in segs).strip()
    fc, ft = entities(text)
    cast = [x for x, _ in fc.most_common(6)]
    terms = [x for x, _ in ft.most_common(6)]
    chapter = pg["part"].split(" ", 1)[-1]

    head = [
        f"# P{n:02d} {pg['part']}",
        "",
        f"- 时长：{fmt_dur(pg['duration'])}　字数：{len(text)}",
        f"- 角色：{'、'.join(f'[{c}](../../characters/{c}.md)' for c in cast) or '—'}",
        f"- 设定：{'、'.join(terms) or '—'}",
        f"- 章节：{season} · {chapter}",
        "",
        "## 正文",
        "",
    ]
    para, paras = [], []
    size = 0
    for s in segs:
        t = (s.get("text") or "").strip()
        if not t:
            continue
        para.append(t)
        size += len(t)
        if size >= 120:
            paras.append("".join(para))
            para, size = [], 0
    if para:
        paras.append("".join(para))

    out_dir = os.path.join(KB, "plot", season)
    os.makedirs(out_dir, exist_ok=True)
    write(os.path.join(out_dir, f"P{n:02d}.md"),
          "\n".join(head) + "\n" + "\n\n".join(paras) + "\n")

    plot_index.append({"page": n, "season": season, "part": pg["part"],
                       "dur": pg["duration"], "chars": len(text),
                       "cast": cast, "terms": terms,
                       "file": f"plot/{season}/P{n:02d}.md"})

    # 检索块：按时间窗 ~350 字
    buf, buf_start, buf_end, buf_len = [], None, None, 0
    for s in segs:
        t = (s.get("text") or "").strip()
        if not t:
            continue
        if buf_start is None:
            buf_start = s.get("start")
        buf.append(t)
        buf_end = s.get("end")
        buf_len += len(t)
        if buf_len >= 350:
            plot_chunks.append({
                "kind": "plot", "title": f"P{n:02d} {pg['part']}",
                "season": season, "episode": n,
                "start": buf_start, "end": buf_end,
                "text": "".join(buf),
            })
            buf, buf_start, buf_end, buf_len = [], None, None, 0
    if buf:
        plot_chunks.append({
            "kind": "plot", "title": f"P{n:02d} {pg['part']}",
            "season": season, "episode": n,
            "start": buf_start, "end": buf_end, "text": "".join(buf),
        })

write(os.path.join(KB, "plot", "索引.md"),
      "# 剧情目录\n\n" + "\n".join(
        f"- [P{x['page']:02d} {x['part']}]({x['file'].replace('plot/','')})（{fmt_dur(x['dur'])}，{x['chars']} 字）"
        for x in plot_index) + "\n")
write(os.path.join(KB, "plot", "_index.json"),
      json.dumps(plot_index, ensure_ascii=False, indent=1))

# ── 4. 切块：wiki 角色 / 世界观 / 剧情 ───────────────────────
chunks = []


def push(kind, title, text, **meta):
    if text and text.strip():
        chunks.append({"kind": kind, "title": title, "text": text.strip(), **meta})


def split_secs(md):
    parts = re.split(r"\n(?=#{2,3} )", md)
    head = parts[0].strip()
    if head:
        yield "总览", head
    for sec in parts[1:]:
        t = sec.split("\n", 1)[0].lstrip("# ").strip()
        yield t, sec.strip()


for path in sorted(glob.glob(os.path.join(KB, "characters", "*.md"))):
    name = os.path.splitext(os.path.basename(path))[0]
    md = read(path)
    for sec_title, sec in split_secs(md):
        if len(sec) <= 600:
            push("character", f"{name} · {sec_title}", sec, entity=name)
        else:
            for i in range(0, len(sec), 500):
                push("character", f"{name} · {sec_title}", sec[i:i + 520], entity=name)

world_files = sorted(glob.glob(os.path.join(KB, "world", "**", "*.md"), recursive=True))
for path in world_files:
    if os.path.basename(path) in ("索引.md",):
        continue
    md = read(path)
    rel = os.path.relpath(path, os.path.join(KB, "world"))
    base = os.path.splitext(rel)[0].replace(os.sep, "/")
    for sec_title, sec in split_secs(md):
        push("world", f"{base} · {sec_title}", sec if len(sec) <= 600 else sec[:600])

chunks.extend(plot_chunks)

# ── 5. 写 chunks.jsonl + SQLite FTS5 ─────────────────────────
with open(os.path.join(KB, "index", "chunks.jsonl"), "w", encoding="utf-8") as f:
    for i, ch in enumerate(chunks):
        ch["id"] = i
        f.write(json.dumps(ch, ensure_ascii=False) + "\n")

db_path = os.path.join(KB, "index", "kb.sqlite")
if os.path.exists(db_path):
    os.remove(db_path)
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("""CREATE TABLE chunks(
  id INTEGER PRIMARY KEY, kind TEXT, title TEXT, season TEXT, episode INTEGER,
  start REAL, end REAL, entity TEXT, text TEXT)""")
cur.execute("CREATE VIRTUAL TABLE fts USING fts5(tok, content='')")
for ch in chunks:
    cur.execute(
        "INSERT INTO chunks(kind,title,season,episode,start,end,entity,text) VALUES(?,?,?,?,?,?,?,?)",
        (ch["kind"], ch["title"], ch.get("season"), ch.get("episode"),
         ch.get("start"), ch.get("end"), ch.get("entity"), ch["text"]))
    rid = cur.lastrowid
    toks = " ".join(t for t in jieba.cut(ch["text"]) if t.strip())
    cur.execute("INSERT INTO fts(rowid, tok) VALUES(?,?)", (rid, toks))
con.commit()

stats = {"chunks": len(chunks), "plot": len(plot_chunks),
         "character": sum(1 for c in chunks if c["kind"] == "character"),
         "world": sum(1 for c in chunks if c["kind"] == "world")}
write(os.path.join(KB, "index", "stats.json"), json.dumps(stats, ensure_ascii=False, indent=1))

print("kb built:", stats)
print("db size MB:", round(os.path.getsize(db_path) / 1048576, 2))
