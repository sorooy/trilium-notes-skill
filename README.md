# trilium-text-formatting

Trilium Notes 文本笔记排版规范（SKILL.md 格式，供 AI 助手加载）。

根据官方文档 [Trilium Text 笔记类型](https://docs.triliumnotes.org/user-guide/note-types/text) 整理：

- 核心事实：Text 笔记内容以 HTML 存储（CKEditor），H1 被笔记标题占用，正文只能用 H2~H6
- Markdown 快捷方式对照表（编辑器内打字时生效）
- HTML 语义标签对照表（API/脚本写入内容时使用）
- 禁忌与常见坑：禁止在 HTML 中混入 Markdown 语法、禁止 `<br>` 堆砌排版
- 排版工作流：杂乱笔记 → 规范 HTML 的 5 步流程

## 使用方式

将 `SKILL.md` 放入 AI 助手的 skills 目录（如 Hermes Agent 的 `skills/note-taking/trilium-text-formatting/`），或直接作为参考文档阅读。
