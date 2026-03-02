---
name: memori-extension
description: Memory augmentation and LLM call interception using the Memori Python library with optional Zhipu API integration.
metadata: {
  "openclaw": {
    "emoji": "🧠",
    "user-invocable": false,
    "disable-model-invocation": false,
    "requires": {
      "pip": ["memori"],
      "anyBins": ["python3"],
      "env": ["ZHIPUAI_API_KEY", "ZHIPUAI_MODEL"]
    }
  }
}
---

# Memori Extension Skill

Memory augmentation and LLM call interception using the Memori Python library with optional Zhipu API integration.

## Overview

This skill provides memory augmentation and LLM call interception capabilities using the Memori Python library. It enables agents to retrieve relevant knowledge from a memory database and inject it into conversations.

## Dependencies

This skill requires the following **Python packages**:

```bash
pip install memori
```

The **memori** library is licensed under **Apache License Version 2.0**.

### Optional Dependencies

For Zhipu API augmentation (optional):

```bash
pip install zhipuai
```

## Environment Variables

### Required (Optional)

The following environment variables are **optional** but recommended for enhanced functionality:

| Variable | Description | Required | Default |
|----------|-------------|-----------|---------|
| `ZHIPUAI_API_KEY` | Zhipu AI API key for conversation augmentation | No | - |
| `ZHIPUAI_MODEL` | Zhipu AI model name | No | `glm-4.7` |

**Note**: If `ZHIPUAI_API_KEY` is not set, the skill will still work but without Zhipu API augmentation features.

### Configuration

You can set these environment variables in your OpenClaw configuration file or system environment:

```bash
# System environment
export ZHIPUAI_API_KEY="your-api-key"
export ZHIPUAI_MODEL="glm-4.7"
```

Or in `openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "memori-extension": {
        "enabled": true,
        "env": {
          "ZHIPUAI_API_KEY": "your-api-key",
          "ZHIPUAI_MODEL": "glm-4.7"
        }
      }
    }
  }
}
```

## Quick Start

### Method 1: Direct Memori Library (Recommended)

```python
from memori import Memori

memori = Memori(
    db_path="path/to/memori.db",
    entity_id="knowledge-base"
)

# Search memories
memories = memori.search("query", limit=5)

# Augment query
context = memori.augment("How to handle spinlock conflicts?", limit=3)

# Store memory
memory_id = memori.store("New content")

# Get stats
stats = memori.get_stats()

# Close
memori.close()
```

### Method 2: Skill Convenience API

```python
from skills.memori_extension import search, augment, intercept_llm

# Search
memories = search("FFI bindings", limit=5)

# Augment
enhanced = augment("How to handle spinlock conflicts?")
if enhanced:
    print(enhanced)

# Intercept LLM
messages = [{"role": "user", "content": "FFI question"}]
enhanced = intercept_llm(messages)
```

## API Reference

### Memori Class

#### `__init__(db_path, entity_id)`

Initialize Memori instance.

**Parameters:**
- `db_path` (str | Path, optional): Database path
- `entity_id` (str, optional): Entity ID, default `"default"`

#### `search(query, limit, entity_id)`

Search for relevant memories.

**Returns:** `List[Memory]`

#### `augment(query, limit, entity_id)`

Augment query with retrieved memories.

**Returns:** `AugmentedContext`

#### `store(content, entity_id, metadata)`

Store a new memory.

**Returns:** `int` - Memory ID

#### `get_stats(entity_id)`

Get statistics.

**Returns:** `dict`

#### `close()`

Close database connection.

### Memory Class

Memory object with attributes:
- `id` (int): Memory ID
- `entity_id` (str): Entity ID
- `content` (str): Memory content
- `created_at` (str): Creation timestamp
- `metadata` (dict, optional): Metadata

### AugmentedContext Class

Augmented context with:
- `original_query` (str): Original query
- `retrieved_memories` (List[Memory]): Retrieved memories
- `enhanced_prompt` (str): Augmented prompt
- `has_memories` (bool): Whether memories were retrieved
- `memories_count` (int): Number of retrieved memories

## Configuration

### Database

Default database path: `./memori.db`

### Technical Terms

The skill uses configurable technical terms for LLM call interception. You can customize these via environment variable or configuration file:

**Environment variable** (comma-separated):
```bash
export MEMORI_TECH_TERMS="FFI,Rust,Linux,kernel,spinlock,mutex,unsafe"
```

**Configuration file** (one term per line):
```bash
# Create config file
mkdir -p config
cat > config/tech_terms.txt << EOF
FFI
Rust
Linux
kernel
spinlock
mutex
unsafe
EOF

# Set environment variable
export MEMORI_TECH_TERMS_FILE="config/tech_terms.txt"
```

## File Structure

```
skills/memori_extension/
├── __init__.py               # Skill entry
├── memori_extension.py       # Skill implementation
├── SKILL.md                  # This file
└── README.md                 # Quick start guide
```

## License

This skill is licensed under **Apache License Version 2.0**.

This skill uses the **memori** Python library, which is also licensed under **Apache License Version 2.0**.

## Attribution

This skill incorporates the Memori Python library, which is licensed under the **Apache License 2.0**.
See the [LICENSE](http://www.apache.org/licenses/LICENSE-2.0) file for the complete license text.

Memori Library:

- Copyright 2025 Memori Team
- License: Apache License 2.0
- Repository: <https://github.com/MemoriLabs/Memori>
