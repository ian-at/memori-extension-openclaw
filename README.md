# Memori Zhipu Skill

Memory augmentation and LLM call interception using the Memori Python library.

## Quick Start

```python
from memori import Memori

memori = Memori(
    db_path="memori.db",
    entity_id="knowledge-base"
)

# Search memories
memories = memori.search("query", limit=5)

# Augment query
context = memori.augment("How to handle spinlock conflicts?", limit=3)

# Store memory
memory_id = memori.store("New content")

# Close
memori.close()
```

## Installation

This skill requires the Memori Python library:

```bash
pip install memori
```

## Usage

### Direct Library Usage

```python
from memori import Memori

memori = Memori(db_path="memori.db", entity_id="knowledge")
memories = memori.search("FFI bindings", limit=5)
memori.close()
```

### Skill API

```python
from skills.memori_zhipu import search, augment, intercept_llm

# Search
memories = search("query", limit=5)

# Augment
enhanced = augment("query")

# Intercept LLM
messages = [{"role": "user", "content": "question"}]
enhanced = intercept_llm(messages)
```

## Dependencies

- **memori** (Apache License 2.0) - Memory management library

## License

This skill is licensed under **Apache License 2.0**.

This skill uses the **memori** Python library, which is also licensed under **Apache License 2.0**.

## Attribution

This skill incorporates the Memori Python library (Apache License 2.0).

See [LICENSE](LICENSE) for full license text.
# memori-extension-openclaw
