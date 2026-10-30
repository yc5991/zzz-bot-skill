# 贡献与二创指南（CONTRIBUTING）

欢迎提交 PR、Issue，或者基于本项目做二创。提交即表示你同意以 **CC BY-NC-SA 4.0** 发布你的贡献。

> English summary at the bottom.

## 可以做

- 修 bug：`rag/tools/query.py`、`build_kb.py`、AGENT 流程里的错误
- 补角色/NPC：新增 `persona.md` + 头像，并更新名册与群聊清单
- 修术语：剧情里的专名、译名、错字
- 翻译：`README.en.md` 或其他语言版本
- 优化检索：分词、切块、时间戳、引用格式
- 补资料：只限你有权使用的内容，并注明来源

## 不可以

- 商用、盈利、付费墙、引流售卖
- 删除或隐藏 `NOTICE.md` 里的作者署名
- **整篇搬运**他人的考据/文章（只能放标题、作者、摘要、原文链接）
- 加入没有授权的图片、音乐、字体、模型
- 破坏 `AGENT.md` 的契约：文件名、字段名、目录结构、建档流程（要改先开 Issue 讨论）
- 让人设 OOC 的改动（与官方档案/剧情明显冲突）

## 具体规则

1. **新增角色**：必须提供 `persona.md` + 头像，头像需有授权；NPC 放 `非代理人/`。
2. **新增资料**：在 `NOTICE.md` 补来源与协议；wiki 文本保持 CC BY-NC-SA 4.0。
3. **考据文章**：只保留标题、作者、摘要、原文链接，不贴全文。
4. **剧情文本**：注明集号/时间戳；不加入未授权的视频全文。
5. **代码**：保持零依赖或写明依赖；`query.py` 必须能在 Python 3.10+ 直接跑。
6. **测试**：至少跑一遍

```bash
pip install jieba
python rag/tools/query.py "零号空洞是什么" --kind world -k 3
```

## 提交流程

1. Fork 本仓库，新建分支（如 `feat/新增角色-xxx`）
2. 只改需要的文件，不要顺手重排全库
3. PR 描述写清：改了什么、为什么、怎么验证、涉及哪些第三方素材
4. 涉及版权的内容，先在 Issue 里说明来源和授权

## Issue 建议格式

- 类型：bug / 内容错误 / 新增角色 / 授权问题 / 其他
- 位置：文件路径或集号
- 现象 / 期望
- 截图或引用（可选）

---

## English summary

Contributions are welcome under **CC BY-NC-SA 4.0**.

- Allowed: bug fixes, docs, new characters/NPCs (with authorized avatars), translations, terminology fixes, retrieval improvements.
- Not allowed: commercial use, removing credits, reposting full third-party articles (summary + link only), unlicensed assets, breaking the `AGENT.md` contract, OOC persona changes.
- Please open an Issue before changing file names, fields, or the build flow.
- Test with `python rag/tools/query.py "零号空洞是什么" --kind world -k 3` before submitting.
