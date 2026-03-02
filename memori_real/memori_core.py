"""
真正的 Memori 集成核心

实现 Memori 的核心功能：
1. 记忆增强（Memory Augmentation）
2. 自动召回（Automatic Retrieval）
3. 实体关系提取（Entity Extraction）
4. 上下文注入（Context Injection）

设计理念：
- 模仿 Memori 的 API 设计
- 兼容 OpenClaw 的架构
- 可选的本地嵌入（无需 OpenAI API）
- 完全可控和可调试
"""
import sqlite3
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict


# ============================================
# 配置
# ============================================

MEMORI_DB_PATH = Path("/home/yishuqi/.openclaw/workspace/memori.db")
ENTITY_ID = "linux-kernel-c2rust-knowledge"
AUGMENTATION_ENABLED = True
RETRIEVAL_ENABLED = True
EMBEDDING_MODEL = "local"  # "local" 或 "openai"


# ============================================
# 数据模型
# ============================================

@dataclass
class Message:
    """消息对象"""
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Memory:
    """记忆对象"""
    id: int
    entity_id: str
    content: str
    embedding: Optional[bytes]  # 向量嵌入
    metadata: Optional[Dict[str, Any]]
    created_at: str
    access_count: int = 0
    last_accessed: Optional[str] = None


@dataclass
class AugmentedContext:
    """增强后的上下文"""
    original_query: str
    retrieved_memories: List[Memory]
    enhanced_prompt: str
    augmentation_metadata: Dict[str, Any]


# ============================================
# Memori 核心
# ============================================

class RealMemori:
    """
    真正的 Memori 集成

    实现 Memori SDK 的核心功能：
    - 记忆存储与检索
    - 自动增强
    - 实体提取
    - 上下文注入
    """

    def __init__(self, db_path: Path = MEMORI_DB_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        """初始化数据库连接"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    # ========================================
    # 1. 记忆存储（Memory Storage）
    # ========================================

    def store_memory(
        self,
        content: str,
        entity_id: str = ENTITY_ID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        存储记忆到数据库

        Args:
            content: 记忆内容
            entity_id: 实体 ID
            metadata: 元数据

        Returns:
            记忆 ID
        """
        cursor = self.conn.cursor()

        # 生成嵌入（如果启用）
        embedding = None
        if EMBEDDING_MODEL == "local":
            # TODO: 实现本地嵌入生成
            pass

        # 插入记忆
        cursor.execute(
            """
            INSERT INTO memori_entity_fact (entity_id, fact, embedding, created_at)
            VALUES ((SELECT id FROM memori_entity WHERE entity_id = ?), ?, ?, ?)
            """,
            (entity_id, content, embedding, datetime.now().isoformat())
        )

        self.conn.commit()
        return cursor.lastrowid

    def store_conversation(
        self,
        messages: List[Message],
        session_id: str,
        augment: bool = True
    ) -> Dict[str, Any]:
        """
        存储对话并执行增强

        Args:
            messages: 消息列表
            session_id: 会话 ID
            augment: 是否执行增强

        Returns:
            增强结果
        """
        # 1. 存储消息到 memori_conversation_message 表
        cursor = self.conn.cursor()

        # 创建或获取会话
        cursor.execute(
            "INSERT OR IGNORE INTO memori_session (session_id, entity_id, process_id) VALUES (?, ?, ?)",
            (session_id, 1, 1)
        )

        # 存储每条消息
        for msg in messages:
            cursor.execute(
                """
                INSERT INTO memori_conversation_message
                (conversation_id, role, type, content, created_at)
                VALUES ((SELECT id FROM memori_conversation WHERE session_id = ?), ?, ?, ?, ?)
                """,
                (session_id, msg.role, "text", msg.content, msg.timestamp)
            )

        self.conn.commit()

        # 2. 执行增强（如果启用）
        augmentation_result = None
        if augment and AUGMENTATION_ENABLED:
            augmentation_result = self._augment_conversation(messages)

        return {
            "session_id": session_id,
            "messages_stored": len(messages),
            "augmentation": augmentation_result
        }

    # ========================================
    # 2. 记忆增强（Memory Augmentation）
    # ========================================

    def _augment_conversation(
        self,
        messages: List[Message]
    ) -> Dict[str, Any]:
        """
        增强对话：提取实体、关系、摘要

        这是 Memori 的核心功能，模仿 memori-sdk 的行为

        Args:
            messages: 对话消息

        Returns:
            增强结果
        """
        # 提取实体（简单版：关键词提取）
        entities = self._extract_entities(messages)

        # 提取关系（简单版：共现分析）
        relations = self._extract_relations(messages)

        # 生成摘要（简单版：最后一条消息）
        summary = messages[-1].content if messages else ""

        # 存储增强结果
        return {
            "entities": entities,
            "relations": relations,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }

    def _extract_entities(self, messages: List[Message]) -> List[str]:
        """提取实体（关键词）"""
        entities = set()

        # 技术关键词
        tech_keywords = [
            "FFI", "bindgen", "spinlock", "mutex", "unsafe",
            "Rust", "Linux", "kernel", "类型", "转换",
            "内存", "并发", "锁", "生命周期"
        ]

        for msg in messages:
            content = msg.content
            for keyword in tech_keywords:
                if keyword.lower() in content.lower():
                    entities.add(keyword)

        return list(entities)

    def _extract_relations(self, messages: List[Message]) -> List[Dict[str, str]]:
        """提取关系（简单版）"""
        relations = []

        # 检测常见模式
        for msg in messages:
            content = msg.content

            # "X 导致 Y" 模式
            if "导致" in content or "因为" in content:
                parts = re.split(r"导致|因为", content)
                if len(parts) == 2:
                    relations.append({
                        "type": "causal",
                        "from": parts[0].strip()[:50],
                        "to": parts[1].strip()[:50]
                    })

        return relations

    # ========================================
    # 3. 记忆召回（Memory Retrieval）
    # ========================================

    def retrieve_memories(
        self,
        query: str,
        limit: int = 5,
        entity_id: str = ENTITY_ID
    ) -> List[Memory]:
        """
        检索相关记忆

        这是 Memori 的核心功能：自动召回

        Args:
            query: 查询文本
            limit: 返回数量
            entity_id: 实体 ID

        Returns:
            相关记忆列表
        """
        if not RETRIEVAL_ENABLED:
            return []

        cursor = self.conn.cursor()

        # 获取实体数据库 ID
        cursor.execute("SELECT id FROM memori_entity WHERE entity_id = ?", (entity_id,))
        entity_row = cursor.fetchone()

        if not entity_row:
            return []

        entity_db_id = entity_row[0]

        # 智能搜索：使用 OR 逻辑（任意关键词匹配）
        search_terms = [t.strip() for t in query.split() if t.strip() and len(t.strip()) > 2]

        if not search_terms:
            return []

        # 构建查询（OR 逻辑）
        clauses = []
        params = [entity_db_id]
        for term in search_terms[:5]:  # 最多 5 个关键词
            clauses.append("fact LIKE ?")
            params.append(f"%{term}%")

        params.append(limit)

        sql = f"""
            SELECT id, entity_id, fact, created_at
            FROM memori_entity_fact
            WHERE entity_id = ? AND ({' OR '.join(clauses)})
            ORDER BY created_at DESC
            LIMIT ?
        """

        cursor.execute(sql, params)
        memories = []

        for row in cursor.fetchall():
            memory = Memory(
                id=row["id"],
                entity_id=entity_id,
                content=row["fact"],
                embedding=None,
                metadata=None,
                created_at=row["created_at"]
            )
            memories.append(memory)

        # 注意：访问统计功能需要额外的列，暂时跳过
        # self._update_access_stats([m.id for m in memories])

        return memories

    def _update_access_stats(self, memory_ids: List[int]):
        """更新记忆访问统计"""
        if not memory_ids:
            return

        cursor = self.conn.cursor()
        for mem_id in memory_ids:
            cursor.execute(
                """
                UPDATE memori_entity_fact
                SET last_accessed = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(), mem_id)
            )

        self.conn.commit()

    # ========================================
    # 4. 上下文增强（Context Enhancement）
    # ========================================

    def augment_query(
        self,
        query: str,
        limit: int = 3
    ) -> AugmentedContext:
        """
        增强查询：检索相关记忆并注入到上下文

        这是 Memori 与 LLM 集成的核心功能

        Args:
            query: 用户查询
            limit: 检索记忆数量

        Returns:
            增强后的上下文
        """
        # 1. 检索相关记忆
        memories = self.retrieve_memories(query, limit=limit)

        # 2. 格式化为上下文
        context_parts = []
        if memories:
            context_parts.append("## 相关记忆 (来自 Memori)\n")
            for i, memory in enumerate(memories, 1):
                context_parts.append(f"### 记忆 {i}")
                context_parts.append(memory.content)
                context_parts.append("")

        memory_context = "\n".join(context_parts)

        # 3. 构建增强提示
        enhanced_prompt = f"""
{memory_context}

用户问题: {query}

请基于以上记忆和你的能力，详细回答用户的问题。
""".strip()

        return AugmentedContext(
            original_query=query,
            retrieved_memories=memories,
            enhanced_prompt=enhanced_prompt,
            augmentation_metadata={
                "memories_count": len(memories),
                "augmentation_time": datetime.now().isoformat()
            }
        )

    # ========================================
    # 5. 统计与管理
    # ========================================

    def get_stats(self) -> Dict[str, Any]:
        """获取 Memori 统计信息"""
        cursor = self.conn.cursor()

        # 统计记忆数量
        cursor.execute("SELECT COUNT(*) as count FROM memori_entity_fact")
        fact_count = cursor.fetchone()["count"]

        # 统计对话数量
        cursor.execute("SELECT COUNT(*) as count FROM memori_conversation")
        conversation_count = cursor.fetchone()["count"]

        # 统计消息数量
        cursor.execute("SELECT COUNT(*) as count FROM memori_conversation_message")
        message_count = cursor.fetchone()["count"]

        return {
            "memories": fact_count,
            "conversations": conversation_count,
            "messages": message_count,
            "db_path": str(self.db_path)
        }

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


# ============================================
# 便捷函数
# ============================================

def create_memori(db_path: Path = MEMORI_DB_PATH) -> RealMemori:
    """
    创建 Memori 实例

    这是与 memori-sdk 兼容的 API
    """
    return RealMemori(db_path)


def augment_and_query(
    query: str,
    memori: Optional[RealMemori] = None
) -> str:
    """
    一站式：增强查询并返回提示

    这是最常用的函数，用于 OpenClaw 集成
    """
    if memori is None:
        memori = create_memori()

    context = memori.augment_query(query)

    return context.enhanced_prompt


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    print("=== 真正的 Memori 集成测试 ===\n")

    # 创建 Memori 实例
    memori = create_memori()

    # 显示统计信息
    stats = memori.get_stats()
    print("Memori 统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    # 测试记忆召回
    test_query = "FFI 绑定中如何处理 spinlock 类型冲突？"
    print(f"测试查询: {test_query}\n")

    context = memori.augment_query(test_query, limit=2)

    print(f"检索到 {len(context.retrieved_memories)} 条记忆\n")
    print("增强后的提示:")
    print("-" * 60)
    print(context.enhanced_prompt[:500] + "...")
    print()

    memori.close()
    print("\n✅ 测试完成")
