# trilium-text-formatting

Trilium Notes 文本笔记排版规范与转换工具（SKILL.md 格式，供 AI 助手加载 + 纯标准库转换脚本）。

根据官方文档 [Trilium Text 笔记类型](https://docs.triliumnotes.org/user-guide/note-types/text) 整理。

---

## 下载与快速开始

### 方式 A：整包下载（推荐）

| 平台 | 命令 / 链接 |
|------|-------------|
| GitHub | `git clone https://github.com/sorooy/trilium-text-formatting.git` 或 [下载 ZIP](https://github.com/sorooy/trilium-text-formatting/archive/refs/heads/main.zip) |
| GitCode | `git clone https://gitcode.com/op00007/trilium-text-formatting.git` 或 [下载 ZIP](https://gitcode.com/op00007/trilium-text-formatting/-/archive/main/trilium-text-formatting-main.zip) |

### 方式 B：只要转换脚本（零依赖）

```bash
# GitHub 或 GitCode 任选其一
curl -O https://raw.githubusercontent.com/sorooy/trilium-text-formatting/main/scripts/md_to_trilium.py
# curl -O https://gitcode.com/op00007/trilium-text-formatting/raw/main/scripts/md_to_trilium.py

python md_to_trilium.py --selftest   # 先自检
```

### 30 秒快速开始

```bash
# 1. 下载后进入项目目录
cd trilium-text-formatting

# 2. 转换你的 Markdown 笔记
python scripts/md_to_trilium.py 我的笔记.md -o out.html

# 3. 写入 Trilium（应用需在运行，Token 在 Options → ETAPI 创建）
curl -X PUT "http://localhost:37840/etapi/notes/<noteId>/content" \
  -H "Authorization: <TOKEN>" -H "Content-Type: text/plain" \
  --data-binary @out.html
```

---

## 1. 有什么能力

**排版规范（SKILL.md）**
- 核心规则：Text 笔记内容以 HTML 存储（CKEditor），**H1 被笔记标题占用**，正文只能用 H2~H6
- Markdown 快捷方式对照表（编辑器内打字时生效）：标题、粗斜删线、列表、待办、引用、代码块、水平线、提示框（admonition）、公式、内部链接等
- HTML 语义标签对照表（API/脚本写入内容时使用）：标题、段落、强调、上下标、颜色、列表、表格、引用、代码、水平线、外部/内部链接
- 禁忌清单：禁止在 HTML 中混入 Markdown 语法（会原样显示）、禁止 `<br>` 堆砌排版、HTML 实体转义
- 完整排版工作流：读取 → 识别结构 → 转换 → 备份 → 写入验证

**转换脚本（scripts/md_to_trilium.py）**
- Markdown → Trilium 兼容 HTML，**标题自动降一级**（`#` → `<h2>`）
- 支持：粗体/斜体/删除线/行内代码、无序/有序列表（含嵌套）、待办（转 ☐/☑）、引用、代码块（自动转义）、水平线、段落
- 纯 Python 标准库，零依赖，Python 3.8+，自带 `--selftest` 自检

**写入通道（配合 trilium-notes skill）**
- ETAPI 优先：`PUT /etapi/notes/{id}/content`（应用运行时，204 = 成功）
- SQLite 兜底：仅限应用未运行时，先备份

---

## 2. 如何使用

### 作为 AI 助手技能
把 `SKILL.md` 放进 AI 助手的 skills 目录后，直接说「整理这篇笔记的排版」，助手会自动按规范处理。

### 手动转换 Markdown
```bash
# 输出 HTML 到终端
python scripts/md_to_trilium.py input.md

# 输出到文件
python scripts/md_to_trilium.py input.md -o out.html

# 运行自检
python scripts/md_to_trilium.py --selftest
```

### 写入 Trilium（应用运行时，ETAPI）
```bash
# 假设已转换出 out.html，替换 <TOKEN> 与 <noteId>
curl -X PUT "http://localhost:37840/etapi/notes/<noteId>/content" \
  -H "Authorization: <TOKEN>" \
  -H "Content-Type: text/plain" \
  --data-binary @out.html
```
Token 在 Trilium 菜单 → Options → ETAPI 创建。

### 转换示例
输入：
```markdown
# 标题一
- 项目 A
  - 子项 1
```
输出：
```html
<h2>标题一</h2>
<ul><li>项目 A<ul><li>子项 1</li></ul></li></ul>
```

---

## 3. 如何安装

### 方式一：Hermes Agent（推荐）
```bash
git clone https://gitcode.com/op00007/trilium-text-formatting.git
# 将整个仓库内容放入 skills 目录（如 D:\Hermes\hermes-data\skills\note-taking\trilium-text-formatting\）
```

### 方式二：其他 AI 助手（Claude Code / Codex / Cursor 等）
将 `SKILL.md` 放入助手的 skills/知识目录，或直接把 `SKILL.md` 作为参考文档引入。

### 方式三：仅用脚本（不装技能）
```bash
# 零依赖，拷贝单个文件即可
curl -O https://gitcode.com/op00007/trilium-text-formatting/raw/main/scripts/md_to_trilium.py
python md_to_trilium.py --selftest
```

### 要求
- Python 3.8+（仅脚本需要，纯标准库无第三方依赖）
- Trilium Notes（写入功能需要，v0.104+ 验证）

---

## 相关

- 配套技能：`trilium-notes`（ETAPI/SQLite 读写、备份、表结构）
- 官方文档：https://docs.triliumnotes.org/user-guide/note-types/text
