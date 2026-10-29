#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown → Trilium 文本笔记 HTML 转换器（纯标准库，无依赖）。

Trilium text note 内容存 HTML（CKEditor），H1 被笔记标题占用，
因此本脚本把 Markdown 标题整体降一级：# → <h2> ... ###### → <h6>。

支持：标题、粗体/斜体/删除线/行内代码、无序/有序列表（含嵌套）、
待办标记（转 ☐/☑ 符号，真待办需在编辑器内插入）、引用、代码块、水平线、段落。

用法：
    python md_to_trilium.py input.md            # 输出 HTML 到 stdout
    python md_to_trilium.py input.md -o out.html
    python md_to_trilium.py 旧.html --from-html -o 新.html   # Markdown 被当文字存进 <p>/<br> 时
    python md_to_trilium.py --selftest          # 自检

写入 Trilium（应用运行时，ETAPI 优先）：
    python -c "import urllib.request; ..."  # 或按 trilium-notes skill 的 PUT 流程
"""
import re
import sys
import html as _html

INLINE_RE = [
    (re.compile(r'\*\*(.+?)\*\*'), r'<strong>\1</strong>'),
    (re.compile(r'__(.+?)__'), r'<strong>\1</strong>'),
    (re.compile(r'(?<!\*)\*([^*\n]+?)\*(?!\*)'), r'<em>\1</em>'),
    (re.compile(r'(?<!_)_([^_\n]+?)_(?!_)'), r'<em>\1</em>'),
    (re.compile(r'~~(.+?)~~'), r'<s>\1</s>'),
    (re.compile(r'`([^`\n]+)`'), r'<code>\1</code>'),
]


def inline(text: str) -> str:
    text = _html.escape(text, quote=False)
    for pat, rep in INLINE_RE:
        text = pat.sub(rep, text)
    return text


def _list_html(items, base):
    """items: [(indent_str, kind, text)]。缩进更深的行作为最后一项的子列表（递归）。"""
    top, sub = [], []
    for ind, kind, text in items:
        if ind == base:
            top.append((kind, text))
        else:
            sub.append((ind, kind, text))
    # 同级别按 kind 分段（ul/ol 混合时各自成块）
    segs, ck, buf = [], None, []
    for kind, text in top:
        if kind != ck:
            if buf:
                segs.append((ck, buf))
            ck, buf = kind, []
        buf.append(text)
    if buf:
        segs.append((ck, buf))
    parts = []
    for k, texts in segs:
        lis = [f'<li>{inline(t)}</li>' for t in texts]
        if sub:
            last = lis.pop()
            lis.append(f'<li>{inline(texts[-1])}{_list_html(sub, sub[0][0])}</li>')
        parts.append(f'<{k}>' + ''.join(lis) + f'</{k}>')
    return ''.join(parts)


def unwrap_html(html_text: str) -> str:
    """把「Markdown 被当文字塞进 <p>/<br>」的存量内容还原成 Markdown 源文本。

    症状：整篇是一堆 <p>## 标题</p>、<p>* 要点<br>* 要点</p>，星号和 # 原样显示。
    """
    s = html_text.replace('&nbsp;', ' ')
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'</p\s*>', '\n', s, flags=re.I)
    s = re.sub(r'<p[^>]*>', '', s, flags=re.I)
    return _html.unescape(s)


def render(blocks: list) -> str:
    out = []
    for kind, data in blocks:
        if kind == 'h':
            lvl = min(data[0] + 1, 6)
            out.append(f'<h{lvl}>{inline(data[1])}</h{lvl}>')
        elif kind == 'p':
            out.append(f'<p>{inline(data)}</p>')
        elif kind == 'blockquote':
            out.append(f'<blockquote>{inline(data)}</blockquote>')
        elif kind == 'admonition':
            t, txt = data
            out.append(f'<aside class="admonition {t}"><p>{inline(txt)}</p></aside>')
        elif kind == 'hr':
            out.append('<hr>')
        elif kind == 'code':
            out.append(f'<pre><code>{_html.escape(data)}</code></pre>')
        elif kind == 'list':
            out.append(_list_html(data, data[0][0]))
    return '\n\n'.join(out)


def parse(text: str) -> list:
    blocks, i, lines = [], 0, text.splitlines()
    buf = []
    codebuf, infence = [], False

    def flush():
        if buf:
            blocks.append(('p', '\n'.join(buf)))
            buf.clear()

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        if infence:
            if stripped.startswith('```'):
                blocks.append(('code', '\n'.join(codebuf)))
                codebuf, infence = [], False
            else:
                codebuf.append(raw)
            i += 1
            continue

        if stripped.startswith('```'):
            flush()
            infence = True
            i += 1
            continue

        if not stripped:
            flush()
            i += 1
            continue

        # 标题：#~###### → h2~h6（降一级）
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            flush()
            blocks.append(('h', (len(m.group(1)), m.group(2))))
            i += 1
            continue

        # 水平线
        if re.match(r'^-{3,}\s*$', line) or re.match(r'^\*{3,}\s*$', line):
            flush()
            blocks.append(('hr', None))
            i += 1
            continue

        # 引用 / 标注块（> [!NOTE] / [!TIP] / [!IMPORTANT] / [!CAUTION] / [!WARNING]）
        if stripped.startswith('>'):
            flush()
            body, kind = [], None
            while i < len(lines) and lines[i].strip().startswith('>'):
                t = lines[i].strip()[1:].strip()
                m = re.match(r'^\[!(\w+)\]\s*$', t)
                if m and kind is None:
                    kind = m.group(1).lower()
                elif t:
                    body.append(t)
                i += 1
            text = ' '.join(body)
            if kind in ('note', 'tip', 'important', 'caution', 'warning'):
                blocks.append(('admonition', (kind, text)))
            else:
                blocks.append(('blockquote', text))
            continue

        # 列表：连续行聚合成 ul/ol（同缩进混合 ul/ol 各自成块，深缩进为子列表）
        m = re.match(r'^(\s*)([-*]|\d+[.)])\s+(.*)$', line)
        if m:
            flush()
            indent, marker, item = m.group(1), m.group(2), m.group(3)
            kind = 'ul' if marker in ('-', '*') else 'ol'
            todo = re.match(r'^\[([ xX])\]\s*(.*)$', item)
            if todo:
                item = ('☑ ' if todo.group(1).lower() == 'x' else '☐ ') + todo.group(2)
            # 收集连续的列表行（含缩进），嵌套交给 _list_html 处理
            items = [(indent, kind, item)]
            j = i + 1
            while j < len(lines):
                mm = re.match(r'^(\s*)([-*]|\d+[.)])\s+(.*)$', lines[j].rstrip())
                if not mm:
                    break
                mk = 'ul' if mm.group(2) in ('-', '*') else 'ol'
                it = mm.group(3)
                tm = re.match(r'^\[([ xX])\]\s*(.*)$', it)
                if tm:
                    it = ('☑ ' if tm.group(1).lower() == 'x' else '☐ ') + tm.group(2)
                items.append((mm.group(1), mk, it))
                j += 1
            blocks.append(('list', items))
            i = j
            continue

        # 普通行 → 段落缓冲
        buf.append(line)
        i += 1

    flush()
    if infence:
        blocks.append(('code', '\n'.join(codebuf)))
    return blocks


def convert(text: str, from_html: bool = False) -> str:
    return render(parse(unwrap_html(text) if from_html else text))


SELFTEST = """# 标题一
## 标题二
正文带 **粗体**、*斜体*、~~删线~~ 和 `代码`。

- 项目 A
- 项目 B
  - 子项 1
  - 子项 2
1. 第一
2. 第二

> 引用一段话

---

```python
print("hi")
```
"""


def selftest():
    out = convert(SELFTEST)
    assert '<h2>标题一</h2>' in out, 'h1 必须降为 h2'
    assert '<h3>标题二</h3>' in out, 'h2 必须降为 h3'
    assert '<strong>粗体</strong>' in out and '<em>斜体</em>' in out
    assert '<s>删线</s>' in out and '<code>代码</code>' in out
    assert '<ul>' in out and '<ol>' in out
    assert '<blockquote>引用一段话</blockquote>' in out

    # GitHub 风格警示块 → Trilium admonition
    adm = convert('> [!WARNING]\n> 这段有坑\n\n> [!NOTE]\n> 补充说明')
    assert '<aside class="admonition warning"><p>这段有坑</p></aside>' in adm, 'admonition warning'
    assert '<aside class="admonition note"><p>补充说明</p></aside>' in adm, 'admonition note'
    assert '<hr>' in out
    assert '<pre><code>print(&quot;hi&quot;)' in out, '代码块内容应做 HTML 转义'
    assert '**粗体**' not in out.replace('<strong>粗体</strong>', ''), '不得残留 Markdown 语法'

    # --from-html：Markdown 被当文字存进 <p>/<br> 的存量内容也能还原
    dumped = ('<p># 标题一<br>* **粗**要点</p><p>&nbsp;* 子项</p><p>---</p>'
              '<p>```text<br>A -&gt; B<br>```</p>')
    out2 = convert(dumped, from_html=True)
    assert '<h2>标题一</h2>' in out2, 'from-html: h1 应降为 h2'
    assert '<li><strong>粗</strong>要点<ul><li>子项</li></ul></li>' in out2, 'from-html: 子项应嵌套'
    assert '<hr>' in out2 and '<pre><code>A -&gt; B</code></pre>' in out2, 'from-html: hr/代码块'
    assert '<br' not in out2 and '<p>#' not in out2, 'from-html: 不得残留 br 或 <p>#'
    print('✅ selftest passed')
    return 0


def main():
    args = sys.argv[1:]
    if '--selftest' in args:
        return selftest()
    if not args:
        print(__doc__)
        return 1
    src = open(args[0], encoding='utf-8').read()
    out = convert(src, from_html='--from-html' in args)
    if '-o' in args:
        open(args[args.index('-o') + 1], 'w', encoding='utf-8').write(out)
    else:
        print(out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
