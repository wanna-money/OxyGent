# Skill Schemas

---
类所在位置：

```
oxygent/schemas/skill.py
```

---

## 简介

本模块定义了 `SkillMetadata`，一个用于技能索引、发现和基于 LLM 的语义匹配的轻量级数据模型。每个技能由一个 `SKILL.md` 文件描述，`SkillMetadata` 捕获该文件的前置元数据（frontmatter），供运行时使用。

## SkillMetadata (BaseModel)

### 参数

| 参数                       | 类型            | 默认值     | 描述                                                            |
| -------------------------- | --------------- | ---------- | --------------------------------------------------------------- |
| `name`                     | `str`           | （必填）   | 唯一的技能标识符。                                              |
| `description`              | `str`           | （必填）   | 用于 LLM 语义匹配的简短描述。                                  |
| `skill_path`               | `Path`          | （必填）   | `SKILL.md` 文件的路径，用于按需加载。                           |
| `version`                  | `Optional[str]` | `None`     | 可选的语义化版本字符串。                                        |
| `author`                   | `Optional[str]` | `None`     | 可选的作者信息。                                                |
| `disable_model_invocation` | `bool`          | `False`    | 若为 true，系统/模型不可自动调用该技能。                        |
| `user_invocable`           | `bool`          | `True`     | 若为 false，用户不可通过 `/skill-name` 手动调用该技能。         |
| `argument_hint`            | `Optional[str]` | `None`     | 可选的用户输入参数提示。                                        |
| `source_name`              | `Optional[str]` | `None`     | 注册此技能的 Skills/SkillHub 组件名称。                         |

### 方法

| 方法                                                   | 协程 (async) | 返回值          | 用途（简述）                                                                   |
| ------------------------------------------------------ | ------------ | --------------- | ------------------------------------------------------------------------------ |
| `from_frontmatter(frontmatter, skill_path)` (classmethod) | 否         | `SkillMetadata` | 工厂方法：从解析后的 YAML frontmatter 创建实例。若缺少 `name` 或 `description` 则抛出 `ValueError`。 |
