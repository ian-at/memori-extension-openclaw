# Memori Zhipu Skill

Memory augmentation and LLM call interception using the Memori Python library.

## License

This skill is licensed under the **Apache License Version 2.0**.

Copyright 2025

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Dependencies

This skill requires the Memori Python library:

```bash
pip install memori
```

The Memori library is licensed under the Apache License Version 2.0.
- Copyright 2025 Memori Team
- Repository: https://github.com/MemoriLabs/Memori

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

## Attribution

This skill incorporates the Memori Python library, which is licensed under the Apache License Version 2.0.

Memori Library:
- Copyright 2025 Memori Team
- License: Apache License 2.0
- Repository: https://github.com/MemoriLabs/Memori

For the complete license text, see:
http://www.apache.org/licenses/LICENSE-2.0
