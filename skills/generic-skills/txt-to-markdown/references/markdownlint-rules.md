# markdownlint Rules Reference

Rules enforced by [DavidAnson/vscode-markdownlint](https://github.com/DavidAnson/vscode-markdownlint) that are most relevant to generated Markdown documents.

---

## Headings

### MD001 — heading-increment
Heading levels must increment by one at a time. You cannot jump from H1 to H3.

```markdown
<!-- Bad -->
# Title
### Section     ← skipped H2

<!-- Good -->
# Title
## Section
### Sub-section
```

### MD003 — heading-style
Always use ATX style (`## Heading`). Never use setext underline style.

```markdown
<!-- Bad (setext) -->
My Heading
----------

<!-- Good (ATX) -->
## My Heading
```

### MD022 — blanks-around-headings
Every heading must be preceded AND followed by a blank line (except at the very top of the file).

```markdown
<!-- Bad -->
Some paragraph text.
## Section Heading
More text here.

<!-- Good -->
Some paragraph text.

## Section Heading

More text here.
```

### MD023 — heading-start-left
Headings must start at column 0. Never indent a heading.

```markdown
<!-- Bad -->
  ## Indented heading

<!-- Good -->
## Heading at column 0
```

### MD025 — single-title
Only one H1 (`# Title`) per document. All other top-level sections use H2 (`## Section`).

### MD026 — no-trailing-punctuation
Headings must not end with `.` `,` `:` `;` `!` `?`.

```markdown
<!-- Bad -->
## Shopping list:

<!-- Good -->
## Shopping List
```

### MD041 — first-line-heading
If the document has a natural title, it should be an H1 on the first line.

---

## Lists

### MD004 — ul-style
Use `-` (dash) for all unordered list items. Never use `*` or `+`.

```markdown
<!-- Bad -->
* Item one
+ Item two

<!-- Good -->
- Item one
- Item two
```

### MD007 — ul-indent
Sub-lists must be indented by exactly 2 spaces per level.

```markdown
<!-- Good -->
- Top level item
  - Sub item (2 spaces)
    - Sub-sub item (4 spaces)
```

### MD029 — ol-prefix
Ordered list items must use sequential numbers.

```markdown
<!-- Bad -->
1. First
1. Second
1. Third

<!-- Good -->
1. First
2. Second
3. Third
```

### MD030 — list-marker-space
Exactly one space after the list marker (`- item`, `1. item`).

### MD032 — blanks-around-lists
Every list block must be preceded and followed by a blank line (unless at the top or bottom of the file).

```markdown
<!-- Bad -->
Some text here.
- Item one
- Item two
More text.

<!-- Good -->
Some text here.

- Item one
- Item two

More text.
```

---

## Code Blocks

### MD031 — blanks-around-fences
Fenced code blocks must be preceded and followed by a blank line.

```markdown
<!-- Bad -->
Some text.
```bash
echo "hello"
```
More text.

<!-- Good -->
Some text.

```bash
echo "hello"
```

More text.
```

### MD040 — fenced-code-language
Always specify a language on fenced code blocks. Use `text` or `plain` for unspecified content.

```markdown
<!-- Bad -->
```
some code
```

<!-- Good -->
```bash
echo "hello"
```
```

### MD046 — code-block-style
Always use fenced code blocks (` ``` `). Never use 4-space or tab indentation for code.

### MD048 — code-fence-style
Always use backticks (` ``` `) for code fences. Never use tildes (`~~~`).

---

## Whitespace

### MD009 — no-trailing-spaces
No trailing spaces at end of lines. (Two trailing spaces for intentional `<br>` breaks are allowed but discouraged — prefer `<br>` tag.)

### MD010 — no-hard-tabs
Use spaces everywhere. No tab characters in the document.

### MD012 — no-multiple-blanks
Never use more than one consecutive blank line.

### MD047 — single-trailing-newline
The file must end with exactly one newline character. No trailing blank lines at end of file.

---

## Emphasis and Inline Formatting

### MD037 — no-space-in-emphasis
No spaces inside emphasis markers.

```markdown
<!-- Bad -->
* some emphasis *

<!-- Good -->
*some emphasis*
```

### MD038 — no-space-in-code
No spaces inside backtick code spans. Spaces *before* the opening backtick (e.g. "word `code`") are allowed. The lint script treats "` and `", "` or `", and "`, `" as false positives and does not flag them.

```markdown
<!-- Bad -->
` some code `

<!-- Good -->
`some code`
```

### MD049 — emphasis-style
Use `*asterisks*` for emphasis (italic), not `_underscores_`.

```markdown
<!-- Bad -->
_italicized text_

<!-- Good -->
*italicized text*
```

### MD050 — strong-style
Use `**double asterisks**` for bold (strong), not `__double underscores__`.

```markdown
<!-- Bad -->
__bold text__

<!-- Good -->
**bold text**
```

---

## Other

### MD035 — hr-style
Horizontal rules must be exactly `---` (three or more dashes, no spaces).

```markdown
<!-- Bad -->
* * *
___
- - -

<!-- Good -->
---
```

### MD036 — no-emphasis-as-heading
Don't use bold text as a substitute for a heading. If it looks like a heading (bold text alone on a line), make it an actual heading.

```markdown
<!-- Bad -->
**Introduction**

Some text here...

<!-- Good -->
## Introduction

Some text here...
```
