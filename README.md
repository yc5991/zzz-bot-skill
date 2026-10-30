# zzz-bot-skill · 绝区零角色 skill

> English: [README.en.md](README.en.md) · 贡献与二创规则：[CONTRIBUTING.md](CONTRIBUTING.md)

## 项目介绍

适用于 **grokbot** 的《绝区零》同人技能包：一次配置，批量创建 **69 位角色 bot**（59 位代理人 + 10 位 NPC），每个 bot 自带官方头像、完整人格档案（persona）、所属势力群聊与主动聊天例程，并接入 grokbot 原生记忆——新艾利都的市民会按自己的性格聊天、串门、吐槽，而不是只会等你开口。

- 市长 bot 读根目录 `AGENT.md` 自动建档：起名、写描述、传资料、拉群
- 玩家可选择扮演**哲**或**铃**（选中一方不建号），也可以都不选、扮演市长旁观

## 快速开始

**方式一：让 grokbot 自己拉取**

直接对 grokbot 说：

```text
拉取并配置这个项目：https://github.com/yc5991/zzz-bot-skill
```

市长 bot 会读 `AGENT.md`，按名册和流程批量建档。

**方式二：发压缩包**

1. 下载本仓库（或 Releases 里的 zip）
2. 把压缩包直接拖给 grokbot
3. 让它解压后先读根目录 `AGENT.md`，再按第 1–14 节执行

配置完成后，先回答它一个问题：**你扮演哲、铃，还是都不选（当市长旁观）？**

## 目录结构

```text
zzz-bot-skill/
├── AGENT.md          市长入口：69 人名册、建档流程、数据库上传、头像、群聊、记忆、例程
├── rag/              知识库
│   ├── world/        世界观、术语、势力、游戏内时间线、16 篇考据摘要
│   ├── characters/   64 张角色卡
│   ├── plot/         77 集主线剧情（已做术语校正）
│   ├── index/        kb.sqlite（FTS5 检索库）
│   └── tools/        query.py 查询脚本
├── 角色目录/         59 位代理人：persona.md + 头像
├── 非代理人/         10 位 NPC：persona.md + 头像 + 人物资料.md
├── README.md
├── LICENSE
└── NOTICE.md
```

## 授权

- **本仓库内容（文档、代码、人设整理、数据组织）：CC BY-NC-SA 4.0**
  署名—非商业性使用—相同方式共享 4.0 国际
- **禁止商用、禁止盈利**
- **允许二创**，但需署名、非商业、并以相同方式共享
- 第三方内容：
  - BWiki 文本：CC BY-NC-SA 4.0
  - 米游社「世界观考据」：仅保留标题/作者/摘要/原文链接，版权归各作者
  - 剧情文本：版权归 miHoYo，视频来源 B站 UP「时生yoy」
  - 角色头像：画师 **@传奇绳匠手撕空洞**（小红书）授权，允许二创、非商业、需署名

完整声明见 [`NOTICE.md`](NOTICE.md)，协议全文见 [`LICENSE`](LICENSE)。

## 致谢

- 游戏原作：miHoYo《绝区零》
- 设定资料：BWiki 绝区零（wiki.biligame.com/zzz）
- 考据文章：米游社「世界观考据」词条下的各位作者
- 剧情视频：B站 UP「时生yoy」
- 角色头像：画师 @传奇绳匠手撕空洞

本项目为粉丝作品，与 miHoYo 无隶属关系，不代表官方。
