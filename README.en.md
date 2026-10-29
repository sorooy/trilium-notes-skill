# trilium-text-formatting

Trilium Notes text note formatting spec & converter — a SKILL.md for AI assistants, plus a pure-stdlib conversion script.

Based on the official docs: [Trilium Text note type](https://docs.triliumnotes.org/user-guide/note-types/text).

**English** | [简体中文](README.md)

> 💡 **SKILL.md is written in Chinese.** For other languages, translate it yourself with any LLM (ChatGPT, DeepSeek, Kimi, etc.): paste the whole `SKILL.md` into the model and ask it to translate while keeping the YAML frontmatter and Markdown structure unchanged.

---

## Download & Quick Start

### Option A: Full package (recommended)

| Platform | Command / Link |
|----------|----------------|
| GitHub | `git clone https://github.com/sorooy/trilium-notes-skill.git` or [Download ZIP](https://github.com/sorooy/trilium-notes-skill/archive/refs/heads/main.zip) |
| GitCode | `git clone https://gitcode.com/op00007/trilium-text-formatting.git` or [Download ZIP](https://gitcode.com/op00007/trilium-text-formatting/-/archive/main/trilium-text-formatting-main.zip) |

### Option B: Script only (zero dependencies)

```bash
# Pick either GitHub or GitCode
curl -O https://raw.githubusercontent.com/sorooy/trilium-text-formatting/main/scripts/md_to_trilium.py
# curl -O https://gitcode.com/op00007/trilium-text-formatting/raw/main/scripts/md_to_trilium.py

python md_to_trilium.py --selftest   # run the self-check first
```

### 30-second quick start

```bash
# 1. Enter the project directory
cd trilium-text-formatting

# 2. Convert your Markdown note
python scripts/md_to_trilium.py my-note.md -o out.html

# 3. Write into Trilium (app must be running; create a token in Options → ETAPI)
curl -X PUT "http://localhost:37840/etapi/notes/<noteId>/content" \
  -H "Authorization: <TOKEN>" -H "Content-Type: text/plain" \
  --data-binary @out.html
```

---

## 1. What it does

**Formatting spec (SKILL.md)**
- Core rules: Text notes store content as HTML (CKEditor). **H1 is reserved for the note title** — use H2~H6 in the body.
- Markdown-like shortcut reference (active while typing in the editor): headings, bold/italic/strike, lists, to-dos, quotes, code blocks, horizontal rule, admonitions, math, internal links, etc.
- HTML semantic tag reference (for writing content via API/scripts, based on real Trilium 0.104.1 editor output): headings, paragraphs, emphasis, super/subscript, text colors, **five `aside.admonition` callouts**, font-size classes, highlight markers, to-dos, tables, collapsible blocks, footnotes, mermaid, anchors, link embeds, page breaks, internal links.
- Pitfalls checklist: never mix Markdown syntax into HTML (it renders literally), never stack `<br>` for layout, always escape HTML entities.
- Full workflow: read → identify structure → convert → backup → write & verify.

**Converter (scripts/md_to_trilium.py)**
- Markdown → Trilium-compatible HTML, **headings auto-shifted down one level** (`#` → `<h2>`).
- Supports: bold/italic/strike/inline code, bullet & numbered lists (nested), to-dos (→ ☐/☑), blockquotes, fenced code (auto-escaped), horizontal rule, paragraphs.
- `--from-html`: repairs legacy notes where Markdown was pasted as plain text inside `<p>`/`<br>`.
- `> [!NOTE]` / `[!TIP]` / `[!IMPORTANT]` / `[!CAUTION]` / `[!WARNING]` → native Trilium admonitions.
- Pure Python standard library, zero dependencies, Python 3.8+, built-in `--selftest`.

**Write channel (pairs with the `trilium-notes` skill)**
- ETAPI first: `PUT /etapi/notes/{id}/content` (while the app is running; 204 = success).
- SQLite fallback: only when the app is closed — always back up first.

---

## 2. How to use

### As an AI assistant skill
Drop `SKILL.md` into your assistant's skills directory, then just say "format this note" — the assistant will follow the spec automatically.

### Convert Markdown manually
```bash
# Print HTML to stdout
python scripts/md_to_trilium.py input.md

# Write to a file
python scripts/md_to_trilium.py input.md -o out.html

# Run the self-check
python scripts/md_to_trilium.py --selftest
```

### Write into Trilium (app running, ETAPI)
```bash
# after converting to out.html, replace <TOKEN> and <noteId>
curl -X PUT "http://localhost:37840/etapi/notes/<noteId>/content" \
  -H "Authorization: <TOKEN>" \
  -H "Content-Type: text/plain" \
  --data-binary @out.html
```
Create the token in Trilium menu → Options → ETAPI.

### Conversion example
Input:
```markdown
# Heading one
- Item A
  - Sub item 1
```
Output:
```html
<h2>Heading one</h2>
<ul><li>Item A<ul><li>Sub item 1</li></ul></li></ul>
```

---

## 3. Installation

### Method 1: Hermes Agent (recommended)
```bash
git clone https://github.com/sorooy/trilium-notes-skill.git
# Put the whole repo into your skills directory (e.g. <your-skills-dir>/note-taking/trilium-text-formatting/)
```

### Method 2: Other AI assistants (Claude Code / Codex / Cursor, etc.)
Put `SKILL.md` into the assistant's skills/knowledge directory, or reference `SKILL.md` directly as a doc.

### Method 3: Script only (no skill install)
```bash
# Zero dependencies — just copy the single file
curl -O https://raw.githubusercontent.com/sorooy/trilium-text-formatting/main/scripts/md_to_trilium.py
python md_to_trilium.py --selftest
```

### Requirements
- Python 3.8+ (script only; pure stdlib, no third-party deps)
- Trilium Notes (only needed for writing; verified on v0.104+)

---

## Related

- Companion skill: `trilium-notes` (ETAPI/SQLite read-write, backup, schema)
- Official docs: https://docs.triliumnotes.org/user-guide/note-types/text
