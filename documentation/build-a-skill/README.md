# Documentation - How To Build A Skill

Details, methodology and GOTCHAs to help you build your own skills.

You can (and should) use Agents and LLMS to help you build efficient skills but you also need to include a variety of sources so that the LLM can build the best possible skill with you.

To better understand the best practice and mechanism implemented in this section, read [the COOL (COntext and Output Libraries) Framework](https://www.linkedin.com/pulse/introducing-context-outputs-library-cool-framework-ai-franck-boullier-9jb9e).

The sources for some of [the skills that are available in this repository](../../skills/README.md) are stored in the [Sources To Build Skills](./sources-to-build-skills/README.md).

## Which LLM and LLM Model To Use To Build A Skill?

DRAFT

Use the best and most recent model you have access to!

END DRAFT

## Which Tool To Use To Build A Skill?

DRAFT

Prefer a tool that lives on your machine and that can read and write files on your machine. This will make the process easier and faster.

### Claude Cowork

<include pros and cons>
<explain that the `.skill` format is actually a `.zip` file>
<explain the weird formatting of the `description` field>

### Cursor

Cursor is my preferred tool to build skills.

<include pros and cons>

END DRAFT

## Example Of Prompt To Help You Build A Skill

```text
Based on the content of the following documents
<document-1>
<document-2>
and based on the official specifications to create a skill
<skill-specification.md>
Can you help me build a skill that does 
<description of the skill you want to build>?
You can use the following existing skills 
<xxx>
<xxx>
If needed, do NOT re-invent these skills!
The input from the user will be
<input description>
The skill should be created in the sub-folder
<path-to-the-sub-folder>
```

## See Also

- [How to install a skill](../install-a-skill/README.md)
- [How to use a skill](../use-skills/README.md)
- [Libraries of skills I have created](../../skills/README.md)
