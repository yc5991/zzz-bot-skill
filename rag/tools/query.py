# -*- coding: utf-8 -*-
"""轻量 RAG 查询：jieba 分词 + SQLite FTS5(BM25)。

用法：
    python tools/query.py "妮可和法厄同是什么关系" -k 5
    python tools/query.py "零号空洞" --kind world -k 8
    python tools/query.py "第三季结局" --season 第三季 --json
"""
import argparse
import json
import os
import re
import sqlite3
import sys

import jieba

HERE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(HERE)
DB = os.path.join(KB, "index", "kb.sqlite")

try:
    GLOSS = json.load(open(os.path.join(KB, "glossary.json"), encoding="utf-8"))
except Exception:
    GLOSS = {"characters": [], "factions": [], "terms": []}

ALIAS = {}
for group in ("characters", "factions", "terms"):
    for e in GLOSS.get(group, []):
        ALIAS[e["canonical"]] = e["canonical"]
        for a in e.get("aliases") or []:
            ALIAS[a] = e["canonical"]

STOP = set("的 了 是 和 与 在 有 我 你 他 她 它 这 那 什么 怎么 为什么 吗 呢 吧 啊 一个 我们 你们 他们".split())


def norm_tokens(q):
    q = q.strip()
    toks = [t.strip() for t in jieba.cut_for_search(q) if t.strip()]
    toks = [t for t in toks if t not in STOP and not re.fullmatch(r"[\W_]+", t)]
    # 别名/规范名互相扩展
    extra = []
    for t in toks:
        if t in ALIAS and ALIAS[t] != t:
            extra.append(ALIAS[t])
    # 整串包含规范名时也补一个
    for canon in ALIAS:
        if len(canon) >= 2 and canon in q and canon not in toks:
            extra.append(canon)
    seen, out = set(), []
    for t in toks + extra:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out[:12]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("-k", type=int, default=6)
    ap.add_argument("--kind", default="", choices=["", "plot", "character", "world"])
    ap.add_argument("--season", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(DB):
        print("没有找到 kb.sqlite，先跑：python rag/tools/build_kb.py", file=sys.stderr)
        return 2

    toks = norm_tokens(args.query)
    if not toks:
        print("查询里没有可用词", file=sys.stderr)
        return 2
    match = " OR ".join('"' + t.replace('"', '""') + '"' for t in toks)

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    season = args.season
    if not season:
        for s in ("第二季尾音", "第一季", "第二季", "第三季"):
            if s in args.query:
                season = s
                break

    where, params = [], []
    if args.kind:
        where.append("c.kind = ?")
        params.append(args.kind)
    if season:
        where.append("c.season = ?")
        params.append(season)

    # “结局/结尾/最后”这类语义词，BM25 排不出来：直接把该季最后一集提前
    ending = any(w in args.query for w in ("结局", "结尾", "最后", "收尾", "终章"))
    order = "s"
    order_params = []
    if ending and season:
        row = con.execute(
            "SELECT MAX(episode) FROM chunks WHERE kind='plot' AND season=?",
            (season,)).fetchone()
        if row and row[0]:
            order = "CASE WHEN c.kind='plot' AND c.episode=? THEN 0 ELSE 1 END, s"
            order_params = [row[0]]

    sql = ("SELECT c.id,c.kind,c.title,c.season,c.episode,c.start,c.end,c.text,"
           "bm25(fts) AS s FROM fts JOIN chunks c ON c.id=fts.rowid "
           "WHERE fts MATCH ? " + (" AND " + " AND ".join(where) if where else "") +
           " ORDER BY " + order + " LIMIT ?")
    params = [match] + params + order_params + [args.k]

    rows = con.execute(sql, params).fetchall()
    if not rows and ending and season:
        # 没有任何“结局”字面命中：退回该季最后一集的最后几块
        row = con.execute(
            "SELECT MAX(episode) FROM chunks WHERE kind='plot' AND season=?",
            (season,)).fetchone()
        if row and row[0]:
            rows = con.execute(
                "SELECT c.id,c.kind,c.title,c.season,c.episode,c.start,c.end,c.text,"
                "0.0 AS s FROM chunks c WHERE c.kind='plot' AND c.season=? AND c.episode=? "
                "ORDER BY c.start DESC LIMIT ?", (season, row[0], args.k)).fetchall()
    out = []
    for r in rows:
        item = {
            "kind": r["kind"], "title": r["title"], "season": r["season"],
            "episode": r["episode"],
            "start": r["start"], "end": r["end"],
            "score": round(-float(r["s"]), 3),
            "text": r["text"],
        }
        out.append(item)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0

    if not out:
        print("（没有命中）")
        return 0
    for i, it in enumerate(out, 1):
        if it["kind"] == "plot":
            ts = ""
            if it["start"] is not None:
                s = int(it["start"])
                ts = f" {s // 60:02d}:{s % 60:02d}"
            src = f"剧情 {it['season']} · {it['title']}{ts}"
        elif it["kind"] == "character":
            src = f"角色卡 · {it['title']}"
        else:
            src = f"世界观 · {it['title']}"
        snippet = it["text"].replace("\n", " ")
        if len(snippet) > 180:
            snippet = snippet[:180] + "…"
        print(f"[{i}] {src}  (score {it['score']})")
        print(f"    {snippet}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
