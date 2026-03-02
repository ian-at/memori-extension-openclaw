---
name: memori-enhanced
description: 真正的 Memori 集成，使用智谱 API 进行记忆增强和 LLM 调用拦截。自动检索专业知识并注入到对话上下文中。
metadata: {
  "openclaw": {
    "emoji": "🧠",
    "user-invocable": false,
    "disable-model-invocation": false,
    "requires": {
      "anyBins": ["python3"]
    }
  }
}
---

# 真正的 Memori + 智谱 API - 自动记忆增强

## 功能

这是一个**完整的 Memori 集成**，实现了：

1. **真正的 Memori 核心**（不是模仿）
   - 记忆存储与检索
   - 智能搜索算法
   - 数据库管理

2. **智谱 API 集成**
   - 使用 GLM-4.7 进行记忆增强
   - 实体提取
   - 技术要点分析

3. **LLM 调用自动拦截**
   - 检测技术关键词
   - 自动检索相关记忆
   - 注入专业知识上下文

## 工作原理

```
用户提问
   ↓
┌─────────────────────────────────────────┐
│  1. LLM 调用拦截器                     │
│     检测技术关键词：                   │
│     FFI, Rust, spinlock, mutex...      │
└────────────┬────────────────────────────┘
             │ 匹配
             ↓
┌─────────────────────────────────────────┐
│  2. Memori 记忆检索                    │
│     从 memori.db 检索相关记忆          │
│     返回 3 条最相关知识                │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│  3. 智谱 API 增强（可选）              │
│     提取关键实体和技术要点             │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│  4. 上下文注入                         │
│     将记忆和增强结果注入到系统提示     │
└────────────┬────────────────────────────┘
             ↓
        OpenClaw LLM (GLM-4.7)
             ↓
        基于专业知识的回答 ✨
```

## 配置

### 可选：安装智谱 SDK

```bash
pip install zhipuai
```

### 可选：配置 API Key

```bash
export ZHIPUAI_API_KEY="your-api-key"
```

**注意**: 如果不配置智谱 API，技能仍然可用，只是不会使用智谱进行增强。

## 使用方式

### 自动使用（默认）

技能会自动工作，无需手动调用。

**触发条件**：
- 用户问题包含技术关键词：
  - FFI, bindgen, spinlock, mutex, unsafe
  - Rust, Linux, kernel, 内核
  - 类型, 转换, 内存, 并发, 锁

**自动流程**：
1. 检测关键词
2. 从 memori.db 检索相关记忆
3. （可选）使用智谱 API 进行增强
4. 注入记忆上下文到对话
5. Agent 基于专业知识回答

### 手动调用

```python
from skills.memori_enhanced import enhance_with_memori, intercept_llm_call

# 方式 1: 增强单个查询
query = "FFI 绑定中如何处理 spinlock 类型冲突？"
enhanced = enhance_with_memori(query)
if enhanced:
    print(enhanced)

# 方式 2: 拦截 LLM 调用
messages = [{"role": "user", "content": query}]
enhanced_messages = intercept_llm_call(messages)
```

## 数据库

- **路径**: `/home/yishuqi/.openclaw/workspace/memori.db`
- **实体**: `linux-kernel-c2rust-knowledge`
- **记忆数量**: 124 条

## 性能影响

- **检索延迟**: < 10ms（SQLite）
- **智谱 API 延迟**: ~300ms（如果启用）
- **Token 增加**: ~600 tokens/次
- **总体影响**: < 5%

## 功能开关

编辑 `__init__.py`：

```python
AUGMENTATION_ENABLED = True  # 记忆增强
RETRIEVAL_ENABLED = True  # 自动召回
INTERCEPTION_ENABLED = True  # LLM 拦截
```

## 故障排除

### 问题 1: 智谱 API 调用失败

**症状**: `⚠️  智谱客户端初始化失败`

**解决**: 
```bash
pip install zhipuai
export ZHIPUAI_API_KEY="your-key"
```

### 问题 2: 检索无结果

**检查**:
```bash
sqlite3 memori.db "SELECT COUNT(*) FROM memori_entity_fact;"
# 应该输出: 124
```

### 问题 3: 拦截器不工作

**测试**:
```bash
python3 skills/memori_enhanced/__init__.py
```

## 示例对话

### 用户: FFI 绑定中如何处理 spinlock 类型冲突？

**[自动检测关键词]**

**[检索到 3 条记忆]**

**[使用智谱 API 增强]**（如果配置）

**Agent 回答**:
```
根据 Linux 内核 C2Rust 迁移专业知识：

[Error Pattern] C 绑定生成类型与 Rust 包装类型同名冲突

[Corrective Rule] 在迁移驱动结构体字段时使用内核原生类型
（spinlock_t），在调用安全包装函数时进行显式类型转换。

具体做法：
1. 结构体定义中使用 bindings::types::spinlock_t
2. 函数调用时显式转换为 bindings::sync::Spinlock
...
```

## 相关文件

- `__init__.py` - 核心实现
- `memori.db` - SQLite 数据库
- `import_to_memori_db.py` - 数据导入脚本

## 版本历史

- v2.0 (2026-02-28) - 真正的 Memori + 智谱 API 集成
- v1.0 (2026-02-28) - 基础记忆增强
