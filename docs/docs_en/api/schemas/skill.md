# Skill Schemas

---
The position of the classes is:

```
oxygent/schemas/skill.py
```

---

## Introduction

This module defines `SkillMetadata`, a lightweight data model for skill indexing, discovery, and LLM-based semantic matching. Each skill is described by a `SKILL.md` file, and `SkillMetadata` captures the frontmatter of that file for runtime use.

## SkillMetadata (BaseModel)

### Parameters

| Parameter                  | Type            | Default    | Description                                                     |
| -------------------------- | --------------- | ---------- | --------------------------------------------------------------- |
| `name`                     | `str`           | (required) | Unique skill identifier.                                        |
| `description`              | `str`           | (required) | Short description for LLM semantic matching.                    |
| `skill_path`               | `Path`          | (required) | Path to the `SKILL.md` file for on-demand loading.              |
| `version`                  | `Optional[str]` | `None`     | Optional semantic version string.                               |
| `author`                   | `Optional[str]` | `None`     | Optional author information.                                    |
| `disable_model_invocation` | `bool`          | `False`    | If true, skill must not be auto-invoked by the system/model.    |
| `user_invocable`           | `bool`          | `True`     | If false, skill must not be manually invoked via `/skill-name`. |
| `argument_hint`            | `Optional[str]` | `None`     | Optional hint for user-provided arguments.                      |
| `source_name`              | `Optional[str]` | `None`     | Name of the Skills/SkillHub component that registered this skill. |

### Methods

| Method                                         | Coroutine (async) | Return Value    | Purpose (concise)                                              |
| ---------------------------------------------- | ----------------- | --------------- | -------------------------------------------------------------- |
| `from_frontmatter(frontmatter, skill_path)` (classmethod) | No      | `SkillMetadata` | Factory: create instance from parsed YAML frontmatter. Raises `ValueError` if `name` or `description` missing. |
