# 聊天窗 / 网页粘贴稿清理（ChatGPT、Gemini、知乎、维基）

目标：只剥壳（DOM 包装、内联样式、编辑器残留），**正文文字逐字不变**。每次写完都用
「去标签取文本 → 压空白 → 比对」自证：`norm(old) == norm(new)`，不等就不许 PUT。

## 判定：这份内容被谁污染了

| 症状 | 来源 | 处理 |
|---|---|---|
| `<div><div>…</div></div>` 多层套壳、`<p><br>&nbsp;</p>` 空占位段 | ChatGPT 网页 | 拆 div、删纯占位 p |
| `<gem-icon-button …>`、`<code-block>`、`<response-element>`、`_ngcontent-*` / `_nghost-*` / `cdk-*` 属性、代码块上孤立的一个 `Plaintext` | Gemini 网页（Angular） | 整元素连内容删（按钮/图标），组件标签只拆壳，`Plaintext` 是语言标签直接删 |
| `data-list-item-id`、`ck-list-marker-*`、`class="ck-*"` | CKEditor 内部标记 | 删属性，标签保留 |
| `<relin-highlight>` / `<relin-origin>` / `<relin-target>` + 大段 `--adj-bg:linear-gradient(…)` | Relingo 翻译插件 | 保留原文词；译注不确定就留 |
| `zhida.zhihu.com/search?...` 链接 + 内嵌 `<svg><path …/></svg>` 星光图标 | 知乎 | 链接降级为纯文字，svg 删 |
| `#cite_note-N` 上标、红链 | 维基剪藏 | 删引用上标/死链，保留词；数学上标（Rⁿ）不动 |

## 安全顺序（顺序错了会互相破坏）

1. **先删整元素**：`gem-icon-button`、`svg`、`script`、`style` —— 它们内部的内容是 UI，不是正文。
2. **再拆壳**：`response-element`、`code-block*`、`div`、`span`（`span` 无属性才拆；有 `style` 的先删属性再拆）。
3. **再删已知属性**：`style` `class` `role` `jslog` `arialabel` `gemtooltip` `type` `size` `fonticonname` `theme`，以及 `_ngcontent-*` `_nghost-*` `cdk-*` `data-*`。
4. **最后删占位段**：`<p[^>]*>(?:\s|<br\s*/?>|&nbsp;)*</p>`。
5. 收尾：`<h4>→<h3>`、`<h3>→<h2>`（**仅当原本没有 h2**，见下）、`<p>\s*</p>` 删空段、`>\s+<` → `><`。

## 坑（每个都真踩过）

- **属性正则绝不能用通配的「连字符词」模式**（如 `[a-z]+-[a-z-]+="[^"]*"`）：它会把 `<span`、`</span` 这类标签名当成属性名连 `<` 一起吃掉，产出 `/span>` 这种碎片，正文跟着错位。只枚举已知属性名。
- **不要用自写 HTMLParser 重建文档**：遇到未闭合的自定义元素（`<response-element>` 之类）栈会错位，产出一堆 `<p><h2>`、`<p><br></p>` 嵌套。正则「拆壳 + 删已知属性」已经够用，坏处小得多。
- **标题降级前先查这篇笔记原本有没有 h2**：已经有「h2 章 + h3 节」两级的笔记（如书摘），再把 h3 统一提成 h2 会把层级压平，所有小节都变成同级。规则：原本无 h2 才 `h3→h2`；原本有 h2 则保持 h2/h3 不动，只清属性。
- **h4 只在有父 h3 时才降成 h3**（如「1. 核心特征」挂在「什么是真正的 MVP？」下面），不要一起提到 h2。
- **纯文本段包 `<p>` 时要按「块内/块外」判断**：行内标签（`strong`/`em`/`a`）的开闭都先攒进缓冲区，遇到块级标签（`p`/`h*`/`ul`/`ol`/`li`/`pre`）才把缓冲区 flush 成 `<p>…</p>`。若在行内元素结束时就 flush，会写出 `<strong><p>…</p></strong>` 这种非法嵌套。
- **`<pre><code>` 里的 ASCII 图（构建-衡量-学习 循环那种）当成正文原样保留**，不要 `>\s+<` 压掉它内部的换行 —— 只对 `pre` 之外做空白压缩。
- **Gemini 代码块的 `Plaintext` 标签**可能紧贴正文（`…闭环运作：Plaintext</p>`），`>Plaintext<` 匹配不到，最后统一 `content.replace('Plaintext','')` 收尾最稳。

## 自检片段

```python
def norm(s):
    import html, re
    return re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', s))).replace('Plaintext', '')
assert norm(old) == norm(new), '文字被改动了，禁止写入'
assert '</span' not in new and 'style=' not in new and 'data-' not in new
assert not re.search(r'<(strong|em|a)><(p|h2|ul|ol|li)', new)
```
