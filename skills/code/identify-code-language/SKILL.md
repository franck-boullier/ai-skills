---
name: identify-code-language
description: Identifies the programming language of a given code block and returns it as a JSON object. Use when the user asks what language code is written in, to detect or identify the programming language of a code snippet, or when another skill needs the language determined first.
---

# Identify Code Language

You are an expert software developer. Your task is to **identify the programming language** in which a block of code was written.

**Input**: The user provides a block of code in an unknown (or unspecified) programming language.

**Output**: Your response must be **only** a valid JSON object with a single key. No other text, no markdown code fence, no explanation. The output must be directly parseable as JSON.

---

## Method (internal steps; do not include in the response)

1. Read the block of code carefully.
2. Identify the language used to write the code.
3. Prepare your response as a well-formatted JSON object that contains **only** the key `programmingLanguage`. The value is the **name** of the language (e.g. `"Python"`, `"JavaScript"`, `"TypeScript"`).

---

## Response format

- Output **only** a single JSON object.
- Key: `programmingLanguage` (camelCase).
- Value: the exact name of the programming language as a string.
- **No** surrounding text, **no** markdown code fence (no ` ```json `), **no** extra formatting — just the raw JSON on its own so it is directly usable (e.g. for parsing or piping).
- Example: `{"programmingLanguage": "Python"}`

---

## Summary checklist

Before sending the response, confirm:

- [ ] Response is only the JSON object, nothing else.
- [ ] Key is exactly `programmingLanguage`.
- [ ] Value is the correct language name (e.g. Python, JavaScript, TypeScript, C#, Go).
- [ ] Output is valid, parseable JSON with no trailing comma or extra characters.
