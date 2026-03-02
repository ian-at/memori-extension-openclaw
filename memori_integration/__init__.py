"""
Memori 知识库集成模块

提供从 Memori SQLite 数据库中检索 Linux 内核 C2Rust 迁移知识的功能。
"""
import sqlite3
from typing import List, Dict, Any
from pathlib import Path


# 数据库配置
MEMORI_DB_PATH = Path("/home/yishuqi/.openclaw/workspace/memori.db")
ENTITY_ID = "linux-kernel-c2rust-knowledge"


def search_memori(query: str, limit: int = 5, entity_id: str = None) -> List[Dict[str, Any]]:
    """
    从 Memori 数据库中搜索相关的知识条目

    Args:
        query: 搜索关键词或问题
        limit: 返回结果的最大数量
        entity_id: 实体 ID（默认使用 linux-kernel-c2rust-knowledge）

    Returns:
        包含知识条目的字典列表，每个字典包含：
        - id: 条目 ID
        - fact: 知识内容
        - created_at: 创建时间
    """
    entity_id = entity_id or ENTITY_ID

    if not MEMORI_DB_PATH.exists():
        return []

    try:
        conn = sqlite3.connect(str(MEMORI_DB_PATH))
        cursor = conn.cursor()

        # 获取实体 ID
        cursor.execute("SELECT id FROM memori_entity WHERE entity_id = ?", (entity_id,))
        entity_row = cursor.fetchone()
        if not entity_row:
            return []

        entity_db_id = entity_row[0]

        # 构建智能搜索查询
        # 1. 直接搜索（所有词都必须匹配）
        # 2. 宽松搜索（任意词匹配）
        search_terms = [t.strip() for t in query.split() if t.strip()]

        if not search_terms:
            return []

        # 构建两种查询模式
        # 模式1: 所有关键词都必须匹配（更精确）
        strict_params = [entity_db_id]
        strict_clauses = []
        for term in search_terms:
            strict_clauses.append("fact LIKE ?")
            strict_params.append(f"%{term}%")

        # 模式2: 任意关键词匹配（更宽松）
        loose_params = [entity_db_id]
        loose_clauses = []
        for term in search_terms:
            loose_clauses.append("fact LIKE ?")
            loose_params.append(f"%{term}%")

        # 先尝试精确搜索
        strict_sql = f"""
            SELECT id, fact, created_at
            FROM memori_entity_fact
            WHERE entity_id = ? AND ({' AND '.join(strict_clauses)})
            ORDER BY created_at DESC
            LIMIT ?
        """
        strict_params.append(limit)

        cursor.execute(strict_sql, strict_params)
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'fact': row[1],
                'created_at': row[2]
            })

        # 如果精确搜索结果不足，补充宽松搜索
        if len(results) < limit:
            remaining = limit - len(results)
            loose_sql = f"""
                SELECT id, fact, created_at
                FROM memori_entity_fact
                WHERE entity_id = ? AND ({' OR '.join(loose_clauses)})
                ORDER BY created_at DESC
                LIMIT ?
            """
            loose_params.append(remaining)

            cursor.execute(loose_sql, loose_params)
            seen_ids = {r['id'] for r in results}
            for row in cursor.fetchall():
                if row[0] not in seen_ids:
                    results.append({
                        'id': row[0],
                        'fact': row[1],
                        'created_at': row[2]
                    })

        conn.close()
        return results

    except Exception as e:
        print(f"Memori 搜索错误: {e}")
        return []


def get_memori_stats(entity_id: str = None) -> Dict[str, Any]:
    """
    获取 Memori 数据库的统计信息

    Returns:
        包含统计信息的字典
    """
    entity_id = entity_id or ENTITY_ID

    if not MEMORI_DB_PATH.exists():
        return {
            'exists': False,
            'path': str(MEMORI_DB_PATH)
        }

    try:
        conn = sqlite3.connect(str(MEMORI_DB_PATH))
        cursor = conn.cursor()

        # 获取实体信息
        cursor.execute("SELECT id FROM memori_entity WHERE entity_id = ?", (entity_id,))
        entity_row = cursor.fetchone()

        if not entity_row:
            conn.close()
            return {
                'exists': True,
                'entity_found': False,
                'entity_id': entity_id
            }

        entity_db_id = entity_row[0]

        # 统计知识条目数
        cursor.execute(
            "SELECT COUNT(*) FROM memori_entity_fact WHERE entity_id = ?",
            (entity_db_id,)
        )
        fact_count = cursor.fetchone()[0]

        # 获取最新条目的时间
        cursor.execute(
            "SELECT MAX(created_at) FROM memori_entity_fact WHERE entity_id = ?",
            (entity_db_id,)
        )
        latest = cursor.fetchone()[0]

        conn.close()

        return {
            'exists': True,
            'entity_found': True,
            'entity_id': entity_id,
            'fact_count': fact_count,
            'latest_entry': latest,
            'path': str(MEMORI_DB_PATH)
        }

    except Exception as e:
        return {
            'exists': True,
            'error': str(e)
        }


def format_memori_result(result: Dict[str, Any]) -> str:
    """
    格式化 Memori 搜索结果为可读文本

    Args:
        result: search_memori() 返回的结果字典

    Returns:
        格式化后的文本
    """
    fact = result.get('fact', '')
    # 已经是格式化好的文本，直接返回
    return fact


def enrich_context_with_memori(query: str, limit: int = 3) -> str:
    """
    从 Memori 中检索相关知识并格式化为上下文文本

    这是为了在 Agent 推理时提供相关的背景知识

    Args:
        query: 用户的查询或问题
        limit: 检索的最大条目数

    Returns:
        格式化的上下文文本，可以直接添加到系统提示中
    """
    results = search_memori(query, limit=limit)

    if not results:
        return ""

    context_parts = []
    context_parts.append("## 相关知识 (来自 Memori 知识库)")
    context_parts.append("")

    for i, result in enumerate(results, 1):
        context_parts.append(f"### 知识条目 {i}")
        context_parts.append(format_memori_result(result))
        context_parts.append("")

    return "\n".join(context_parts)


if __name__ == "__main__":
    # 测试代码
    print("=== Memori 知识库集成测试 ===\n")

    # 显示统计信息
    stats = get_memori_stats()
    print(f"数据库状态: {stats}\n")

    # 测试搜索
    test_queries = [
        "FFI 绑定类型转换",
        "spinlock mutex",
        "内联函数 宏"
    ]

    for query in test_queries:
        print(f"\n搜索: {query}")
        print("-" * 50)
        results = search_memori(query, limit=2)
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] {result['fact'][:200]}...")
