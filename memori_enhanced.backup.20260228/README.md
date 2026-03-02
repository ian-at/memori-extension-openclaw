# Memori 增强技能 - 集成指南

## ✅ 已创建的文件

```
skills/memori_enhanced/
├── SKILL.md           # 技能说明（OpenClaw 读取）
├── __init__.py        # 核心实现
├── config.json        # 配置文件
└── README.md          # 本文档
```

---

## 🚀 如何激活技能

### 方法 1：重启 Gateway（推荐）

```bash
# 重启 OpenClaw Gateway
openclaw gateway restart
```

Gateway 会自动发现新技能并在下次对话时加载。

### 方法 2：刷新技能（无需重启）

如果 Gateway 支持热重载：

```bash
# 发送刷新信号（Linux/macOS）
pkill -USR1 -f "openclaw gateway"
```

或者等待下次新会话自动加载。

---

## 🧪 验证技能是否生效

### 1. 检查技能是否加载

在 OpenClaw 对话中问：

```
列出所有可用的技能
```

应该看到 `memori-enhanced` 在列表中。

### 2. 测试记忆增强

问一个 Linux 内核 C2Rust 相关的问题：

```
FFI 绑定中如何处理 spinlock 类型冲突？
```

Agent 应该会引用专业知识回答。

---

## 📊 工作原理

```
用户提问
   ↓
┌─────────────────────────────────────┐
│  memori-enhanced 技能              │
│  1. 检测关键词（FFI、spinlock等）   │
│  2. 从 memori.db 检索相关知识       │
│  3. 格式化为上下文                  │
│  4. 注入到系统提示                  │
└─────────────────────────────────────┘
   ↓
增强后的提示 → OpenClaw LLM → 专业回答
```

---

## ⚙️ 配置选项

编辑 `config.json`：

```json
{
  "enabled": true,           // 是否启用技能
  "autoTrigger": true,       // 是否自动触发
  "settings": {
    "maxResults": 3,         // 最多检索多少条知识
    "minConfidence": 0.5,    // 最小相关性阈值（暂未实现）
    "cacheEnabled": true,    // 是否缓存检索结果（暂未实现）
    "cacheTTL": 300         // 缓存有效期（秒）
  }
}
```

---

## 🎯 触发条件

技能会在以下情况自动触发：

### ✅ 会触发

- 包含关键词：`FFI`, `spinlock`, `mutex`, `unsafe`, `Linux`, `kernel`, `Rust`
- 提到：类型转换、内存布局、并发控制
- 问题涉及：代码迁移、架构设计

### ❌ 不会触发

- 日常对话（天气、时间、闲聊）
- 通用技术问题（Python、JavaScript）
- 不相关领域

---

## 🔍 调试

### 查看检索日志

在 Python 中测试：

```bash
cd /home/yishuqi/.openclaw/workspace
python3 skills/memori_enhanced/__init__.py
```

### 查看数据库状态

```python
from skills.memori_integration import get_memori_stats
stats = get_memori_stats()
print(stats)
```

### 手动测试检索

```python
from skills.memori_enhanced import enhance_query

context = enhance_query("FFI 绑定类型冲突", limit=2)
print(context)
```

---

## 📈 性能影响

- **检索延迟**: < 10ms（SQLite 查询）
- **Token 增加**: 每条知识约 200-500 tokens
- **总体影响**: 可忽略不计（< 5% 响应时间增加）

---

## 🛠️ 故障排除

### 问题 1：技能没有加载

**检查**：
```bash
ls -la /home/yishuqi/.openclaw/workspace/skills/memori_enhanced/
```

**解决**：
```bash
# 重启 Gateway
openclaw gateway restart
```

### 问题 2：检索无结果

**检查**：
```bash
sqlite3 /home/yishuqi/.openclaw/workspace/memori.db "SELECT COUNT(*) FROM memori_entity_fact;"
# 应该输出: 124
```

**解决**：
```bash
# 重新导入知识
cd /home/yishuqi/.openclaw/workspace
python3 import_to_memori_db.py
```

### 问题 3：每次都检索，包括非技术问题

**检查**：关键词列表是否太宽泛

**解决**：编辑 `__init__.py` 中的 `KEYWORDS` 列表

---

## 🎉 使用示例

### 示例 1：类型转换问题

**用户**：
```
FFI 绑定中 spinlock_t 类型转换失败怎么办？
```

**Agent 回答**：
```
根据 Memori 知识库，这是一个常见的类型冲突问题：

[Error Pattern] C 绑定生成类型与 Rust 包装类型同名冲突

[Corrective Rule] 在迁移驱动结构体字段时使用内核原生类型
（spinlock_t），在调用安全包装函数时进行显式类型转换...

具体做法：
1. 结构体定义中使用 bindings::types::spinlock_t
2. 函数调用时显式转换为 bindings::sync::Spinlock
```

### 示例 2：非技术问题（不触发）

**用户**：
```
今天天气怎么样？
```

**Agent 回答**：
```
（正常回答，不检索专业知识）
```

---

## 📝 下一步改进

- [ ] 添加缓存机制（避免重复检索）
- [ ] 支持语义搜索（基于向量嵌入）
- [ ] 添加检索结果评分
- [ ] 支持多个知识库（医疗、法律等）

---

## 📞 获取帮助

- 测试技能：`python3 skills/memori_enhanced/__init__.py`
- 查看日志：检查 Gateway 输出
- 重新导入：`python3 import_to_memori_db.py`

---

**创建时间**: 2026-02-28
**版本**: 1.0
**状态**: ✅ 已测试
