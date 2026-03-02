# Memori 知识库集成

这是一个自定义技能，用于集成 Memori 知识库到 OpenClaw Agent 推理流程中。

## 功能

在 Agent 推理时自动从 Memori 数据库中检索相关的 Linux 内核 C2Rust 迁移知识。

## 位置

所有脚本位于: `/home/yishuqi/.openclaw/workspace/`

## 数据库

- **路径**: `/home/yishuqi/.openclaw/workspace/memori.db`
- **实体**: `linux-kernel-c2rust-knowledge`
- **知识条目**: 124 条

## 使用方式

### 1. 手动检索

```python
from skills.memori_integration import search_memori

# 搜索相关知识
results = search_memori("FFI 绑定类型转换", limit=5)
for result in results:
    print(result['fact'])
```

### 2. 在 Agent 提示中自动检索

当 Agent 遇到 Linux 内核 C2Rust 相关问题时，可以：

1. 识别关键词（如 "FFI"、"bindgen"、"类型转换"）
2. 自动调用 `search_memori()` 检索相关知识
3. 将检索结果作为上下文添加到提示中

### 3. 配置文件

可以在 OpenClaw 配置中添加 Memori 作为扩展记忆源：

```yaml
memori:
  db_path: /home/yishuqi/.openclaw/workspace/memori.db
  entity_id: linux-kernel-c2rust-knowledge
  enabled: true
```

## 知识覆盖范围

- **FFI 绑定** (ffi): 类型转换、结构体映射、函数指针
- **架构设计** (architecture): 构建系统、模块依赖、内存布局
- **迁移规则** (migration): 依赖分析、前置检查
- **代码风格** (code-style): unsafe 块、错误处理
- **并发控制** (concurrency): 锁机制、等待队列
- **生命周期** (lifecycle): 初始化、资源管理

## 检索策略

1. **关键词匹配**: 在 Domain、Category、Error Pattern 中查找
2. **语义搜索**: 使用全文搜索找到相关内容
3. **上下文排序**: 根据相关性和重要性排序

## 维护

- 添加新知识: 使用 `import_to_memori_db.py` 脚本
- 更新现有知识: 直接修改数据库或重新导入
- 备份数据库: 复制 `memori.db` 文件
