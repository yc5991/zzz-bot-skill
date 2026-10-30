# zzz-bot-skill · Zenless Zone Zero Character Skill

A fan-made skill pack for **grokbot**: configure once and batch-create **69 character bots** (59 agents + 10 NPCs) from *Zenless Zone Zero*. Each bot ships with an official-style avatar, a full persona, faction group chats, a proactive-chat routine, and access to grokbot's native memory — so New Eridu feels alive instead of waiting for you to speak first.

- The mayor bot reads `AGENT.md` and builds everything: names, descriptions, data upload, avatars, groups
- You can play as **Wise** or **Belle** (the chosen sibling is not created as a bot), or pick neither and watch as the mayor

## Quick Start

**Option 1 — let grokbot pull it**

Tell grokbot:

```text
拉取并配置这个项目：https://github.com/yc5991/zzz-bot-skill
```

The mayor bot will read `AGENT.md` and build the roster.

**Option 2 — send the archive**

1. Download this repository (or the zip from Releases)
2. Drag the archive into grokbot
3. Ask it to unzip and read `AGENT.md` first, then follow sections 1–14

After setup, answer one question: **play as Wise, Belle, or neither (watch as the mayor)?**

## Layout

```text
zzz-bot-skill/
├── AGENT.md          Mayor entry: roster, build flow, data upload, avatars, groups, memory, routines
├── rag/              Knowledge base
│   ├── world/        Worldview, glossary, factions, in-game timeline, 16 article summaries
│   ├── characters/   64 character cards
│   ├── plot/         77 episodes of main-story transcript (term-corrected)
│   ├── index/        kb.sqlite (FTS5 search index)
│   └── tools/        query.py
├── <character>/      59 agents: persona.md + avatar
├── 非代理人/          10 NPCs: persona.md + avatar + profile
├── README.md         Chinese README
├── README.en.md      This file
├── CONTRIBUTING.md   Contribution / derivative-work rules
├── LICENSE
└── NOTICE.md
```

## License

- **Project content (docs, code, persona compilation, data organization): CC BY-NC-SA 4.0**
  Attribution–NonCommercial–ShareAlike 4.0 International
- **No commercial use, no profit**
- **Derivative works are allowed**, with attribution, non-commercial use, and the same license
- Third-party notices:
  - BWiki text: CC BY-NC-SA 4.0
  - Miyoushe articles: title/author/summary/link only; copyright belongs to their authors
  - Story text: copyright miHoYo; source video by Bilibili creator "时生yoy"
  - Character avatars: authorized by artist **@传奇绳匠手撕空洞** (Xiaohongshu); derivatives allowed, non-commercial, attribution required

See [`NOTICE.md`](NOTICE.md) for details and [`LICENSE`](LICENSE) for the full text.

## Credits

- Original game: miHoYo — *Zenless Zone Zero*
- Lore reference: BWiki ZZZ (wiki.biligame.com/zzz)
- Articles: the authors of Miyoushe's "Worldview Research" entries
- Story video: Bilibili creator "时生yoy"
- Character avatars: artist @传奇绳匠手撕空洞

This is a fan project, not affiliated with or endorsed by miHoYo.
