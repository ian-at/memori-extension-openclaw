---
name: memori-enhanced
description: 自动从 Memori 知识库检索相关知识并注入到对话上下文中，增强 Agent 回答的专业性。
metadata: {
  "openclaw": {
    "emoji": "🧠",
    "user-invocable": false,
    "disable-model-invocation": false
  }
}
---

# Memori 增强技能

## 功能

在每次对话开始时，自动从 Memori 知识库检索相关知识，并将其注入到系统提示中，使 Agent 能够基于专业知识回答问题。

## 工作流程

1. **检测用户查询主题**
   - 判断是否与 Linux 内核 C2Rust 迁移相关
   - 提取关键关键词

2. **检索相关知识**
   - 调用 `search_memori()` 从数据库检索
   - 返回最相关的 3-5 条知识

3. **增强上下文**
   - 将知识格式化为系统提示
   - 注入到对话开始

4. **调用 LLM**
   - 使用增强后的提示调用模型
   - Agent 基于专业知识回答

## 何时使用

**自动触发**（无需手动调用）：
- 用户提到 Linux 内核、Rust、FFI、迁移等关键词
- 问题涉及代码转换、类型绑定、架构设计
- 技术问题需要专业知识

**关键词示例**：
- FFI、bindgen、cbindgen
- spinlock、mutex、并发
- 类型转换、内存布局
- 不透明指针、C 绑定
- unsafe、生命周期

## 实现细节

### 检索逻辑

```python
# 从 skills/memori_integration 导入
from skills.memori_integration import search_memori

# 搜索相关知识（智能匹配）
results = search_memori(query, limit=3)
```

### 上下文注入

检索到的知识会被格式化为：

```markdown
## 相关专业知识 (来自 Memori 知识库)

### 知识 1
[Domain: linux-kernel-c2rust]
[Category: ffi]
[Error Pattern] C 绑定生成类型与 Rust 包装类型同名冲突导致类型转换失败

[Root Cause] bindgen 生成的内核原生类型（如 bindings::types::spinlock）
与安全包装类型（如 bindings::sync::spinlock）命名相同但语义不同...

[Corrective Rule] 在迁移驱动结构体字段时使用内核原生类型（如 spinlock_t），
在调用安全包装函数时进行显式类型转换...
```

## 配置

可以通过以下方式调整行为：

### 修改检索数量

编辑 `skills/memori_integration/__init__.py`：

```python
def search_memori(query: str, limit: int = 5):  # 改为 5
```

### 添加更多关键词

编辑本文件，在"关键词示例"部分添加。

## 数据库

- **路径**: `/home/yishuqi/.openclaw/workspace/memori.db`
- **实体**: `linux-kernel-c2rust-knowledge`
- **知识条目**: 124 条

## 性能影响

- **检索时间**: < 10ms（SQL 查询）
- **Token 增加**: 每条知识约 200-500 tokens
- **总体影响**: 可忽略不计

## 维护

### 查看数据库状态

```python
from skills.memori_integration import get_memori_stats
stats = get_memori_stats()
print(stats)
```

### 添加新知识

```bash
cd /home/yishuqi/.openclaw/workspace
python3 import_to_memori_db.py
```

### 重建索引

```bash
sqlite3 memori.db "CREATE INDEX IF NOT EXISTS fact_search ON memori_entity_fact(fact);"
```

## 故障排除

### 检索无结果

1. 确认数据库存在：
   ```bash
   ls -lh /home/yishuqi/.openclaw/workspace/memori.db
   ```

2. 验证知识条目：
   ```bash
   sqlite3 /home/yishuqi/.openclaw/workspace/memori.db "SELECT COUNT(*) FROM memori_entity_fact;"
   ```

3. 测试检索：
   ```python
   from skills.memori_integration import search_memori
   results = search_memori("FFI", limit=3)
   print(len(results))
   ```

### 性能问题

如果检索变慢，可以：
1. 添加全文索引（见上方"重建索引"）
2. 减少 limit 参数
3. 优化关键词提取

## 相关文件

- `skills/memori_integration/__init__.py` - 检索 API
- `skills/memori_integration/SKILL.md` - 集成文档
- `import_to_memori_db.py` - 导入脚本
- `memori.db` - SQLite 数据库

## 版本历史

- v1.0 (2026-02-28) - 初始版本，自动记忆增强
