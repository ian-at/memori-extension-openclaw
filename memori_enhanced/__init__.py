"""
真正的 Memori 集成 - 使用智谱 API

这是一个完整的 Memori 实现，包含：
1. 记忆存储与检索
2. 智谱 API 增强功能
3. LLM 调用自动拦截
4. 上下文自动注入

这是升级版的 memori-enhanced，现在是真正的 Memori 集成。
"""
import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# 尝试导入智谱 SDK
try:
    from zhipuai import ZhipuAI
    ZHIPUAI_AVAILABLE = True
except ImportError:
    ZHIPUAI_AVAILABLE = False
    print("⚠️  zhipuai 未安装，将使用基础模式")

# ============================================
# 配置
# ============================================

MEMORI_DB_PATH = Path("/home/yishuqi/.openclaw/workspace/memori.db")
ENTITY_ID = "linux-kernel-c2rust-knowledge"

# 智谱 API 配置
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
ZHIPUAI_MODEL = os.getenv("ZHIPUAI_MODEL", "glm-4.7")

# 功能开关
AUGMENTATION_ENABLED = True
RETRIEVAL_ENABLED = True
INTERCEPTION_ENABLED = True


# ============================================
# 数据模型
# ============================================

@dataclass
class Memory:
    """记忆对象"""
    id: int
    content: str
    created_at: str


@dataclass
class AugmentedContext:
    """增强后的上下文"""
    original_query: str
    retrieved_memories: List[Memory]
    enhanced_prompt: str
    used_zhipu: bool


# ============================================
# 智谱 AI 客户端
# ============================================

class ZhipuAIClient:
    """智谱 AI 客户端"""

    def __init__(self, api_key: str = None):
        if not ZHIPUAI_AVAILABLE:
            self.client = None
            return

        self.api_key = api_key or ZHIPUAI_API_KEY
        if not self.api_key:
            self.client = None
            return

        try:
            self.client = ZhipuAI(api_key=self.api_key)
        except Exception as e:
            print(f"⚠️  智谱客户端初始化失败: {e}")
            self.client = None

    def is_available(self) -> bool:
        """检查客户端是否可用"""
        return self.client is not None

    def enhance(self, text: str) -> str:
        """使用智谱 API 增强文本"""
        if not self.is_available():
            return None

        try:
            response = self.client.chat.completions.create(
                model=ZHIPUAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是专业的技术分析助手。"},
                    {"role": "user", "content": f"请提取以下文本中的关键实体和技术要点：\n\n{text}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️  智谱 API 调用失败: {e}")
            return None


# ============================================
# Memori 核心
# ============================================

class RealMemori:
    """真正的 Memori 核心"""

    def __init__(self, db_path: Path = MEMORI_DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        
        # 智谱客户端
        self.zhipu = ZhipuAIClient()

    def retrieve_memories(
        self,
        query: str,
        limit: int = 3,
        entity_id: str = ENTITY_ID
    ) -> List[Memory]:
        """检索相关记忆"""
        if not RETRIEVAL_ENABLED:
            return []

        cursor = self.conn.cursor()

        # 获取实体 ID
        cursor.execute("SELECT id FROM memori_entity WHERE entity_id = ?", (entity_id,))
        entity_row = cursor.fetchone()
        if not entity_row:
            return []

        entity_db_id = entity_row[0]

        # 构建搜索查询
        search_terms = [t.strip() for t in query.split() if t.strip() and len(t.strip()) > 2]
        if not search_terms:
            return []

        # OR 查询
        clauses = []
        params = [entity_db_id]
        for term in search_terms[:5]:
            clauses.append("fact LIKE ?")
            params.append(f"%{term}%")

        params.append(limit)

        sql = f"""
            SELECT id, fact, created_at
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
                content=row["fact"],
                created_at=row["created_at"]
            )
            memories.append(memory)

        return memories

    def augment_query(
        self,
        query: str,
        limit: int = 3,
        use_zhipu: bool = True
    ) -> AugmentedContext:
        """增强查询：检索记忆并使用智谱 API 增强"""
        # 检索记忆
        memories = self.retrieve_memories(query, limit=limit)

        # 使用智谱 API 增强（如果可用）
        zhipu_enhancement = None
        if use_zhipu and self.zhipu.is_available() and memories:
            memory_text = "\n".join([m.content for m in memories])
            zhipu_enhancement = self.zhipu.enhance(memory_text)

        # 格式化上下文
        context_parts = []
        if memories:
            context_parts.append("## 相关记忆 (来自 Memori 知识库)\n")
            for i, memory in enumerate(memories, 1):
                context_parts.append(f"### 记忆 {i}")
                context_parts.append(memory.content)
                context_parts.append("")

        # 如果有智谱增强，添加它
        if zhipu_enhancement:
            context_parts.append("\n## 智谱 AI 增强分析\n")
            context_parts.append(zhipu_enhancement)
            context_parts.append("")

        memory_context = "\n".join(context_parts)

        # 构建增强提示
        enhanced_prompt = f"""{memory_context}
用户问题: {query}

请基于以上记忆和你的能力，详细回答用户的问题。
""".strip()

        return AugmentedContext(
            original_query=query,
            retrieved_memories=memories,
            enhanced_prompt=enhanced_prompt,
            used_zhipu=zhipu_enhancement is not None
        )

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM memori_entity_fact")
        fact_count = cursor.fetchone()["count"]

        return {
            "memories": fact_count,
            "db_path": str(self.db_path),
            "zhipu_enabled": self.zhipu.is_available()
        }

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()


# ============================================
# LLM 调用拦截器
# ============================================

class LLMInterceptor:
    """LLM 调用拦截器"""

    # 技术关键词
    KEYWORDS = [
        "FFI", "bindgen", "spinlock", "mutex", "unsafe",
        "Rust", "Linux", "kernel", "内核", "迁移",
        "类型", "转换", "内存", "并发", "锁",
        "生命周期", "cbindgen"
    ]

    def __init__(self, memori: RealMemori):
        self.memori = memori
        self.intercept_count = 0

    def should_intercept(self, messages: List[Dict[str, str]]) -> bool:
        """判断是否应该拦截"""
        if not INTERCEPTION_ENABLED:
            return False

        # 检查用户消息
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "").lower()
                # 检查关键词
                return any(kw.lower() in content for kw in self.KEYWORDS)

        return False

    def intercept_and_enhance(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """拦截并增强消息"""
        # 提取用户查询
        user_query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_query = msg.get("content", "")
                break

        if not user_query:
            return messages

        # 使用 Memori 增强查询
        context = self.memori.augment_query(user_query, limit=3)

        if not context.retrieved_memories:
            return messages

        # 构建增强消息
        enhanced_messages = [
            {
                "role": "system",
                "content": f"""你是一个专业的技术助手。请参考以下专业知识回答用户问题：

{context.enhanced_prompt}
"""
            }
        ]

        # 添加原始消息
        for msg in messages:
            if msg.get("role") != "system":
                enhanced_messages.append(msg)

        self.intercept_count += 1
        return enhanced_messages


# ============================================
# 全局实例
# ============================================

_memori_instance = None
_interceptor_instance = None


def get_memori() -> RealMemori:
    """获取全局 Memori 实例"""
    global _memori_instance
    if _memori_instance is None:
        _memori_instance = RealMemori()
    return _memori_instance


def get_interceptor() -> LLMInterceptor:
    """获取全局拦截器实例"""
    global _interceptor_instance
    if _interceptor_instance is None:
        _interceptor_instance = LLMInterceptor(get_memori())
    return _interceptor_instance


# ============================================
# 公共 API
# ============================================

def enhance_with_memori(query: str) -> Optional[str]:
    """
    使用 Memori 增强查询
    
    Args:
        query: 用户查询
        
    Returns:
        增强后的提示，如果不需要增强则返回 None
    """
    memori = get_memori()
    context = memori.augment_query(query)

    if context.retrieved_memories:
        return context.enhanced_prompt
    else:
        return None


def intercept_llm_call(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    拦截 LLM 调用并自动增强
    
    Args:
        messages: 原始消息列表
        
    Returns:
        增强后的消息列表
    """
    interceptor = get_interceptor()
    
    if interceptor.should_intercept(messages):
        return interceptor.intercept_and_enhance(messages)
    else:
        return messages


# ============================================
# 测试
# ============================================

if __name__ == "__main__":
    print("=== 真正的 Memori + 智谱 API 集成测试 ===\n")

    # 创建 Memori
    memori = get_memori()
    stats = memori.get_stats()

    print("Memori 状态:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    # 测试增强
    test_query = "FFI 绑定中如何处理 spinlock 类型冲突？"
    print(f"测试查询: {test_query}\n")

    context = memori.augment_query(test_query)

    print(f"✅ 检索到 {len(context.retrieved_memories)} 条记忆")
    print(f"智谱增强: {'✅' if context.used_zhipu else '❌'}")
    print()

    print("增强后的提示:")
    print("-" * 60)
    print(context.enhanced_prompt[:500] + "...")
    print()

    # 测试拦截
    print("\n=== 测试 LLM 调用拦截 ===\n")

    test_messages = [
        {"role": "user", "content": "FFI 绑定中如何处理 spinlock 类型冲突？"}
    ]

    enhanced = intercept_llm_call(test_messages)

    print(f"原始消息: {len(test_messages)} 条")
    print(f"增强后: {len(enhanced)} 条")
    print(f"拦截次数: {get_interceptor().intercept_count}")

    if len(enhanced) > len(test_messages):
        print("\n✅ 拦截成功，已注入记忆上下文")
    else:
        print("\n❌ 未拦截（可能不包含技术关键词）")

    memori.close()
    print("\n✅ 测试完成")
