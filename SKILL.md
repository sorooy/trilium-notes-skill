---
name: trilium-text-formatting
description: 整理/生成 Trilium 文本笔记排版内容时使用。官方 HTML 结构 + Markdown 快捷方式规范。
version: 1.2.0
author: sorooy
platforms: [windows]
---

# Trilium 文本笔记排版

根据官方文档 https://docs.triliumnotes.org/user-guide/note-types/text 整理的排版规范。
当需要「整理/排版 Trilium 笔记内容」「把杂乱文本或 Markdown 转成 Trilium 富文本」「生成可写入 Trilium 的 content」时使用本 skill。读写 API / SQLite 操作见 `trilium-notes` skill。

## 核心事实（必须先知道）

1. **Text note 是 Trilium 默认笔记类型**，内容以 **HTML** 存储（blobs.content，mime=`text/html`），编辑器是 CKEditor（所见即所得 WYSIWYG）。
2. **H1 被笔记标题占用了！** 正文内标题只能用 **H2 ~ H6**。H1 不会出现在格式列表里。
3. 字号是**相对值**（Tiny/Small/Normal/Large 等），不是像素数。别用大字号代替标题。
4. 通过 API / 数据库写入内容时，写入的是**纯 HTML** —— 编辑器里的 Markdown 快捷方式**不会生效**，必须直接写标准 HTML。
5. 官方支持的完整功能：通用格式（标题/字号/粗斜下删线/上下标/字体色/背景色）、列表（无序/有序/待办/可折叠嵌套）、引用 & 提示框、表格（合并/样式/标题/透明边框布局）、代码（行内/块/快捷键）、脚注、图片、外部链接 & 内部链接、Include Note（嵌入笔记）、插入按钮（符号/数学公式 KaTeX/Mermaid 图/水平线/分页符）、缩进、Markdown 导入、剪为子笔记；Premium：斜杠命令/模板/格式刷。

## Markdown 快捷方式（编辑器内打字时生效 — 仅作参考，不写入内容）

| 输入 | 效果 |
|------|------|
| `##`~`######` + 空格 | H2~H6 标题 |
| `**text**` / `__text__` | 粗体 |
| `*text*` / `_text_` | 斜体 |
| `~~text~~` | 删除线 |
| `* ` 或 `- ` | 无序列表 |
| `1. ` 或 `1) ` | 有序列表 |
| `[ ]` / `[x]` | 待办（未完成/完成） |
| `[/]` / `[?]` / `[-]` | 待办扩展状态：进行中/考虑中/已取消 |
| `> ` | 引用块 |
| ` ``` ` | 代码块 |
| `---` | 水平线 |
| `!!! note/tip/important/caution/warning` | 提示框（admonition） |
| `:emoji名` | 表情自动补全 |
| `$$` 或 `\[`、`Ctrl+M` | 数学公式（TeX / KaTeX） |
| `@` 或 `Ctrl+L` | 内部笔记链接 |
| `Ctrl+Shift+Enter` | 循环切换任务状态 |
| `Ctrl+Shift+V` | 粘贴为纯文本（去掉外来格式） |

不想触发自动格式时按 `Ctrl+Z` 还原。

## HTML 排版规则（写入内容的正确姿势）

### 语义标签对照表

| 需求 | 用这个 HTML |
|------|-------------|
| 标题 | `<h2>` ~ `<h6>`（**禁止 h1**，留给笔记标题） |
| 段落 | `<p>` |
| 粗体 / 斜体 / 下划线 / 删除线 | `<strong>` / `<em>` / `<u>` / `<s>` |
| 上标 / 下标 | `<sup>` / `<sub>`（单位 cm³、化学式 NaHCO₃） |
| 字体颜色 / 背景色 | `<span style="color:#e74c3c">` / `<span style="background-color:#fff3cd">` |
| 无序列表 / 有序列表 | `<ul><li>` / `<ol><li>`，嵌套直接套 |
| 引用块 | `<blockquote>`（内部可放表格、图片、再嵌套引用/提示框） |
| 行内代码 / 代码块 | `<code>` / `<pre><code>` |
| 表格 | `<table><thead><tbody><tr><th><td>`，说明文字用 `<caption>` |
| 水平线 | `<hr>` |
| 外部链接 | `<a href="https://...">` |
| 内部链接（镜像标题） | `<a class="reference-link" href="#root/{noteId}">` |
| 内部链接（自定义文字） | `<a href="#root/{noteId}">自定义文字</a>` |
| 分页（打印/PDF） | 编辑器 Insert → Page break（HTML 结构由插件生成） |

### 禁忌（常见坑）

- ❌ **不要把 Markdown 语法写进 HTML 内容**（`**粗体**`、`## 标题`、`* 列表`、`> 引用` 会**原样显示**，不渲染！）
- ❌ **不要用 `<br>` 堆砌做排版**（`<br><br><br>` 分层），用真实的块级标签
- ❌ 不要用 `<h1>`（冲突笔记标题）
- ✅ 转义 HTML 实体：`&` → `&amp;`，`<` → `&lt;`，`>` → `&gt;`
- ✅ 中英混排注意空格；强调用粗体/颜色而非满屏大字号

### 提示框（Admonition）要点

- 五种类型：`note` / `tip` / `important` / `caution` / `warning`（灵感来自 GitHub，不可自定义）
- 功能上≈引用块但样式不同；可容纳标题、表格、图片等任意块级内容
- 空提示框按 Backspace 删除；Enter 两次跳出

### 其他官方设计原则

- **折叠块**（Insert → Collapsible Block）：隐藏细节，多个连续放置=手风琴效果；`Ctrl+Enter` 展开/收起；适合 FAQ
- **可折叠嵌套列表**（v0.104+）：列表项有子项时悬停出现箭头，`Ctrl+Alt+Enter` 切换折叠
- **透明边框表格**：Table properties → Style=Single、Color=transp，可做无边框栅格布局
- **脚注**：正文放引用标记，内容显示在笔记底部，适合补充说明
- **待办扩展状态**：进行中 `[/]`、考虑中 `[?]`、取消 `[-]`（可自定义），勾选框单击只在 无↔完成 间切换
- **Math**：TeX 格式，KaTeX 渲染；行内 `$...$`、块级 `$$...$$`（Display mode 居中）
- **内部链接**：@ 或 Ctrl+L 插入；"Link title mirrors" 类型会跟随笔记标题变化；复制笔记树节点 Ctrl+C 后 Ctrl+V 粘贴也能生成链接
- 大笔记会只读打开；配色注意深/浅主题对比度

## ⚠️ 铁律：排版不改内容

**只改结构/格式，绝不增删改原文文字。**

- ❌ 不删除、不合并、不重写任何原文内容（含标题文字、列表项、段落、标点）
- ❌ 不添加原文没有的内容（不补全、不扩写、不「优化措辞」）
- ✅ 允许的改动仅限：标签语义化（`<div><strong>` → `<h2>`）、清理格式污染（`data-list-item-id`、`ck-*`、`relin*` 等样式残留）、实体转义、中英间空格规范化
- ⚠️ 插件注入的译注（如 Relingo 的 `(我)/(独家)` 等**插入内容**）与原文混在一起时：默认保留原文词，译注属插件添加物，可删可不删——不确定时保留，宁多勿删

## 排版工作流（整理一个杂乱笔记）

1. 读取原内容（**优先 ETAPI**：`GET /etapi/notes/{id}/content`；应用未运行时才走 SQLite，见 `trilium-notes` skill 的铁律）
2. 识别结构：标题层级、列表、引用、代码、表格、待办
3. 转成上面的语义 HTML：
   - Markdown `##` → `<h2>`（**整体降一级**：原 `#` 标题 → `<h2>`，因为 h1 留给笔记标题）
   - `**x**` → `<strong>x</strong>`，`*x*` → `<em>x</em>`
   - `- ` / `1. ` → `<ul>/<ol>` + `<li>`（嵌套缩进 → 嵌套列表）
   - `> ` → `<blockquote>`，`!> ` 或 `!!!` → 提示框（若已知结构）
   - 反引号块 → `<pre><code>`，行内 `` ` `` → `<code>`
   - `---` → `<hr>`
   - 表格管道语法 → `<table>`
4. 写入前**备份**（文档 `.db.backup_时间戳` 或导出）
5. 写入并验证（**回读走 API** `GET /etapi/notes/{id}/content` 确认应用真实状态，不要只看数据库）

## 一键转换脚本（scripts/md_to_trilium.py）

纯标准库，把 Markdown 转成 Trilium 兼容 HTML（标题自动降一级、列表嵌套、待办转 ☐/☑、代码块转义）：

```bash
python scripts/md_to_trilium.py input.md            # 输出 HTML
python scripts/md_to_trilium.py input.md -o out.html
python scripts/md_to_trilium.py --selftest          # 自检
```

转换结果可直接 `PUT /etapi/notes/{id}/content` 写入。局限：真待办/表格/提示框的插件专属 HTML 需编辑器内插入或手工写。

## 关联

- `trilium-notes`：API / SQLite 读写、Token、备份、表结构
- 官方文档：https://docs.triliumnotes.org/user-guide/note-types/text （含子页面 general-formatting / lists / tables / blockquotes / markdown-formatting / collapsible-blocks / math-equations / todo-lists / footnotes / insert-buttons）
