# Memori Extension Skill

Memory augmentation and LLM call interception using the Memori Python library with optional Zhipu API integration.

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

This skill requires the **Memori Python library**:

```bash
pip install memori
```

The Memori library is licensed under the Apache License Version 2.0.

### Optional: Zhipu API

For enhanced conversation augmentation, you can optionally install the Zhipu AI SDK:

```bash
pip install zhipuai
```

## Environment Variables

### Optional Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|-----------|---------|
| `ZHIPUAI_API_KEY` | Zhipu AI API key for conversation augmentation | No | - |
| `ZHIPUAI_MODEL` | Zhipu AI model name | No | `glm-4.7` |
| `MEMORI_TECH_TERMS` | Comma-separated technical terms for LLM interception | No | - |
| `MEMORI_TECH_TERMS_FILE` | Path to file containing technical terms (one per line) | No | `./config/tech_terms.txt` |

### Configuration Examples

**System environment:**
```bash
export ZHIPUAI_API_KEY="your-api-key"
export ZHIPUAI_MODEL="glm-4.7"
```

**OpenClaw configuration (`openclaw.json`):**
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

**Technical terms file:**
```bash
# Create config directory
mkdir -p config

# Create terms file
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

## Quick Start

### Installation

```bash
# Install Memori library (required)
pip install memori

# Install Zhipu SDK (optional)
pip install zhipuai
```

### Basic Usage

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

### Using the Skill API

```python
from skills.memori_extension import search, augment, intercept_llm

# Search memories
memories = search("query", limit=5)

# Augment query
enhanced = augment("query")
if enhanced:
    print(enhanced)

# Intercept LLM calls
messages = [{"role": "user", "content": "question"}]
enhanced_messages = intercept_llm(messages)
```

## Features

- ✅ **Memory retrieval** - Search knowledge database by keywords
- ✅ **Query augmentation** - Inject retrieved memories into conversation
- ✅ **LLM call interception** - Automatically enhance LLM calls
- ✅ **Configurable terms** - Customize technical keywords for interception
- ✅ **Optional Zhipu API** - Enhanced conversation analysis (requires API key)

## Attribution

This skill incorporates the Memori Python library, which is licensed under the Apache License Version 2.0.

**Memori Library:**
- Copyright 2025 Memori Team
- License: Apache License 2.0
- Repository: https://github.com/MemoriLabs/Memori

**Full license text:** http://www.apache.org/licenses/LICENSE-2.0
