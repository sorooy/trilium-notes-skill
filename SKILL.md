---
name: trilium-text-formatting
description: 整理/生成 Trilium 文本笔记排版时用。h2 起标、纯 HTML、排版不改内容。
version: 2.4.0
author: sorooy
platforms: [windows]
---

# Trilium 排版规范 v2.0

整理/生成 Trilium 文本笔记内容时使用。读写通道（ETAPI/SQLite）见 `trilium-notes`。

## 一、铁律（违反即返工）

1. **禁 H1**：正文从 `<h2>` 起，向下 `h3`~`h6`。标题由笔记树管理，正文出现 `#` 或 `<h1>` 一律算错。
2. **不改内容**：只动结构/标签/层级/样式。**不增删、不改写、不精简、不总结、不补全**原文（含标题文字、列表项、标点）。
3. **层级只补不压**：原本没有 h2 的才 `h3→h2`；原本已是「h2 章 + h3 节」的保持两级。压平已有层级 = 无声改结构。
4. **写入前自证**：去标签取文本 → 压白 → `norm(old) == norm(new)`；不等不许写。写完回读复查。
5. **HTML 与 Markdown 不混**：存进笔记的必须是 HTML；Markdown 语法出现在内容里会**原样显示**。

## 二、两种写入形态（别搞混）

| 场景 | 能用的语法 |
|---|---|
| **在 Trilium 编辑器里打字** | Markdown 快捷方式生效：`##`+空格→h2、`**粗**`、`- `、`> `、```` ``` ````、`#标签`、`@` 内部链接 |
| **走 API / 脚本写入**（`PUT /etapi/notes/{id}/content`） | **只能纯 HTML**。`## 标题`、`**粗**`、`#type=note` 全部原样当文字存，不会渲染、不会生成属性 |

> 实测：API 写入 `<p>#probe=1 #type=note</p>` 后回读，笔记属性为空 —— 行内 `#标签` 只在编辑器输入时被解析。要设属性请 `POST /etapi/attributes`（见 `trilium-notes`）。

## 三、语义标签表（Trilium 0.104.1 真实标记）

> 下表不是猜的：来自编辑器实际产出的 HTML（用户「格式示例」笔记）+ `app.asar` 里的 CSS 定义。

| 需求 | Trilium 真实标记 |
|---|---|
| 标题 | `<h2>`~`<h6>`（禁 h1） |
| 段落 / 粗斜下划线删除 | `<p>` `<strong>` `<em>` `<u>` `<s>` |
| 上标 / 下标 | `<sup>` `<sub>` |
| 字色 | `<span style="color:#c0392b">` |
| **警示块** | `<aside class="admonition note"><p>…</p></aside>` — 五色，自带图标+边框 |
| 高亮底色 | `<span style="background-color:hsl(30,75%,60%)">`；或语义类 `marker-yellow` `marker-green` `marker-pink` `marker-blue`（#fdfd77 / #62f962 / #fc7899 / #72ccfd） |
| 字号 | `<span class="text-tiny">`.7em、`text-small`.85em、`text-big`1.4em、`text-huge`1.8em |
| 引用 | `<blockquote><p>…</p></blockquote>` |
| 列表 | `<ul><li>` / `<ol><li>`；圆点 `<ul style="list-style-type:circle;">` |
| **待办** | `<ul class="todo-list"><li data-list-item-id="…"><label class="todo-list__label"><input type="checkbox" disabled><span class="todo-list__label__description">文字</span></label></li></ul>` |
| 代码 | `<pre><code class="language-text-plain">…</code></pre>`；`language-mermaid` 自动渲染成图 |
| 表格 | `<figure class="table"><table><tbody><tr><td>…</td></tr></tbody></table></figure>` |
| 折叠块 | `<details class="trilium-collapsible" open=""><summary>标题</summary><p>内容</p></details>` |
| 脚注 | 正文：`<span class="footnote-reference" data-footnote-index="1" data-footnote-id="abc"><sup><a href="#fnabc">[1]</a></sup></span>`；文末：`<ol class="footnote-section footnotes"><li class="footnote-item" data-footnote-index="1" data-footnote-id="abc" id="fnabc"><span class="footnote-back-link"><sup><strong><a href="#fnrefabc">^</a></strong></sup></span><div class="footnote-content"><p>脚注内容</p></div></li></ol>` |
| 内部链接 | `<a class="reference-link" href="#root/{noteId}">文字</a>` |
| 书签锚点 | 锚点 `<a id="{书签id}"></a>` + 笔记标签 `#internalBookmark={书签id}` |
| 外链卡片 | `<section class="link-embed" data-url="https://…" data-embed-type="opengraph" data-title="标题">&nbsp;</section>` |
| 分页符 | `<div class="page-break" style="page-break-after:always;"><span style="display:none;">&nbsp;</span></div>` |
| 缩进 | `<p style="margin-left:40px;">` |
| 水平线 | `<hr>` |
| 外部链接 | `<a href="https://...">` |
| 图片 | `<img src="api/attachments/{attachmentId}/image/文件名.jpg">` |

## 四、标准结构模板

```html
<h2>核心概述</h2>
<p>一句话点明主题。</p>

<h2>详细内容</h2>
<h3>1. 子模块 / 概念</h3>
<ul>
<li>要点一</li>
<li>要点二
  <ul><li>细分颗粒度</li></ul>
</li>
</ul>

<h3>2. 代码或结构化数据</h3>
<pre><code>// 代码片段</code></pre>

<h2>相关链接与参考</h2>
<ul>
<li><a href="#root/目标笔记id">关联笔记标题</a></li>
</ul>
```

**模板修正（两处硬伤）**：
- `[[关联笔记标题]]` 是 **Obsidian/wiki 语法，Trilium 不识别**，必须写成 `<a href="#root/{noteId}">`。
- 顶部 `#type=note #status=active` 只能在编辑器里打出来才成属性；脚本请走 API。

## 五、禁止清单

- ❌ `<h1>` / 正文 `#` 标题
- ❌ 内容里残留 Markdown（`## 标题`、`**粗**`、`* 列表`、`> 引用`、` ``` `）
- ❌ 用 `<br><br><br>` 堆叠替代块级元素
- ❌ 跳级（h2 直接到 h4）
- ❌ `[[双链]]`（Obsidian 语法）
- ❌ 改字：润色、合并句子、补“更严谨”的说法、删重复段落
- ✅ 转义：`&`→`&amp;`、`<`→`&lt;`、`>`→`&gt;`

## 六、清理粘贴残留（详见 references/paste-cleanup.md）

### 情况 A：Markdown 被当文字存进去（最常见）

**症状**：内容是一堆 `<p>`，里面还带着 `# `/`## `/`* `/`1. `/`---`/`` ``` ``，星号和 # 在笔记里**原样显示**，整个笔记是一大块字（从聊天窗/文档粘进编辑器时选“纯文本”就会这样）。

一条命令解决：

```bash
python scripts/md_to_trilium.py 旧内容.html --from-html -o 新内容.html
```

它把 `<p>`/`<br>` 拆回 Markdown 行（`&nbsp;` 缩进还原），再走正常转换：标题整体降一级（`#`→h2、`##`→h3、`###`→h4，保持相对层级不压平）、`*`→`<ul>`、缩进项→嵌套列表、`1.`→`<ol>`、`---`→`<hr>`、` ``` `→`<pre><code>`。

写完必须比文本：去标签去标记后**逐字相等**才算过（差异只允许出现在 `---`、`1.` 序号、`**` 标记上）。

### 情况 B：平台垃圾（聊天窗/网页带样式复制）

从聊天窗/网页复制来的稿子必带垃圾，按此顺序处理：

1. 清平台专属组件：Gemini 的 `<gem-icon-button>` `<code-block>` `<response-element>` `_ngcontent-*` `Plaintext`；CKEditor 的 `data-list-item-id` `ck-*`；Relingo 的 `relin-*`
2. 拆包装：`<div>` `<span>`（无样式意义的）
3. 只删**已知属性名**（style/class/role/jslog/data-*/_ngcontent-*）——用通配正则 `[a-z]+-[a-z-]+="..."` 会吞掉标签本体
4. 删空占位段落 `<p><br>&nbsp;</p>`
5. 最后才调层级

> **两个坑（都踩过）**：
> 1. Trilium 编辑器会在你打开/编辑笔记后给每个 `<li>` 加上 `data-list-item-id="..."` —— 这是**它自己的标记，不是粘贴垃圾**，不要清；下次编辑还会加回来。脚本里匹配列表项必须用 `<li[^>]*>` 而不是 `<li>`。
> 2. 处理嵌套列表时不能用 `<li>(.*?)</li>` non-greedy 包整段——它会在子项的第一个 `</li>` 就截断，导致子项漏处理。正确做法：逐个匹配 `<li[^>]*>` 开头，只看其后的首个子标签（`<strong>`/`<em>`）来决定怎么处理。

> 自写 HTMLParser 重建结构容易错位（<p> 套 <h2>、嵌套 <p><br></p>）。优先「正则清垃圾 + 轻量包裹裸文本」，不要过度工程。

## 七、工作流

1. `GET /etapi/notes/{id}/content` 读原文（应用未运行才走 SQLite）
2. 记下原有标题层级（决定能否升级）
3. 清垃圾 → 补结构 → 比对文本
4. 写入（`Content-Type: text/plain`）→ 回读验证

## 八、视觉层次（按内容选手段）

优先级：**警示块 > 字号 > 颜色**。颜色是最弱的手段，放最后。

### 1. 警示块 `aside.admonition`（首选）

五种，自带图标 + 左边框，跟随主题：

| class | 色 | 用在 |
|---|---|---|
| `note` | 蓝 #69c7ff | 补充说明、背景信息 |
| `tip` | 绿 #40c025 | 技巧、经验、推荐做法 |
| `important` | 紫 #9839f7 | 必须知道的约束、前提 |
| `caution` | 红 #ff2e2e | 高风险操作、易错点 |
| `warning` | 琥珀 #e2aa03 | 反例、陷阱、警告 |

```html
<aside class="admonition warning"><p>反例：以“好/坏”道德标准划分，缺乏客观衡量依据。</p></aside>
```

Markdown 里写 `> [!WARNING]` + `> 内容`，脚本自动转成对应 admonition（`--selftest` 有覆盖）。

### 2. 字号（做注解、降噪）

`text-small`（.85em）适合脚注式补充，`text-tiny`（.7em）适合来源标注，`text-big/huge` 用于强调数字或结论。

### 3. 颜色（只给标签，不给整句）

| 色 | 色值 | 给谁 |
|---|---|---|
| 红 | `#c0392b` | 风险、反例、陷阱、警惕、杜绝、失职 |
| 蓝 | `#2c6fbb` | 标准、要求、衡量、核心路径、定义 |
| 绿 | `#218868` | 结论、洞见、推荐做法 |

```html
<li><strong><span style="color:#c0392b">警惕数字陷阱</span></strong>：数字具有欺骗性…</li>
```

**别做**：一屏三种颜色全用满；整句上色；给每个 li 都加 admonition（那就没有重点了）。

### 4. 引用 / 折叠 / 高亮

- `<blockquote>` 只给**定义句 / 出处 / 原话**，不给正文段落
- `<details class="trilium-collapsible">` 收**长例子 / 补充材料 / 操作步骤**，`<summary>` 写明收起的是什么
- 高亮底色用 `marker-yellow/green/pink/blue` 语义类，全文 ≤3 处

## 九、编辑器内标准模板（Markdown，手打时用）

在 Trilium 编辑器里新建笔记时，直接粘这段（`#标签` 会变成属性，`##` 会变成标题）：

````markdown
#type=note #status=active #version=2.0
---

## 核心概述
[简要点明主题]

## 详细内容层级
### 1. 子模块 / 概念
* 详细要点 1
* 详细要点 2
  * 细分颗粒度

### 2. 代码或结构化数据
```language
// 代码片段
```

## 相关链接与参考
* [[笔记标题]] → 手打时用 @ 选目标笔记
````

要点：
- 首行 `#type=note #status=active #version=2.0` 只有在**编辑器输入**时才变属性；用脚本写入无效（见第二节）
- `---` 手打才变分隔线；HTML 里对应 `<hr>`
- `[[双链]]` Trilium 不认，手打用 `@` 或 `Ctrl+L` 拾内部链接
- 同一套结构若要脚本批量复用，用第四节的 HTML 版

## 十、脚本

```bash
python scripts/md_to_trilium.py input.md -o out.html            # Markdown → Trilium HTML（标题自动降一级）
python scripts/md_to_trilium.py 旧.html --from-html -o 新.html    # 情况 A：Markdown 被当文字塞进 <p>/<br>
python scripts/md_to_trilium.py --selftest
```

## 关联

- **实地样张**：笔记「Trilium 排版样式速查（演示）」`hLfAvps7Ip5U`（警示块/字号/高亮/待办/折叠/mermaid 全套可见效果），「格式示例」`O8OVVQHYG3Ae`（编辑器原生输出原稿）
- `references/paste-cleanup.md`：各类粘贴源判定表 + 安全处理顺序 + 踩过的坑
- `trilium-notes`：ETAPI 端点、属性/附件、备份
- 官方文档：https://docs.triliumnotes.org/user-guide/note-types/text
