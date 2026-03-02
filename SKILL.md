---
name: memori-zhipu
description: Memory augmentation and LLM call interception using the Memori Python library.
metadata: {
  "openclaw": {
    "emoji": "🧠",
    "user-invocable": false,
    "disable-model-invocation": false,
    "requires": {
      "pip": ["memori"],
      "anyBins": ["python3"]
    }
  }
}
---

# Memori Zhipu Skill

Memory augmentation and LLM call interception using the Memori Python library.

## Overview

This skill provides memory augmentation and LLM call interception capabilities using the Memori Python library.

## Dependencies

This skill requires the **memori** Python package:

```bash
pip install memori
```

The **memori** library is licensed under **Apache License Version 2.0**.

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
from skills.memori_zhipu import search, augment, intercept_llm

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

### Zhipu API (Optional)

If using Zhipu API for augmentation:

```bash
pip install zhipuai
export ZHIPUAI_API_KEY="your-api-key"
```

## File Structure

```
skills/memori_zhipu/
├── __init__.py               # Skill entry
├── memori_zhipu.py           # Skill implementation
├── SKILL.md                  # This file
└── README.md                 # Quick start guide
```

## License

This skill is licensed under **Apache License Version 2.0**.

This skill uses the **memori** Python library, which is also licensed under **Apache License Version 2.0**.

## Attribution

This skill incorporates the Memori Python library, which is licensed under the **Apache License 2.0**.
See the [LICENSE](LICENSE) file for the complete license text.

Memori Library:

- Copyright 2025 Memori Team
- License: Apache License 2.0
- Repository: <https://github.com/MemoriLabs/Memori>
