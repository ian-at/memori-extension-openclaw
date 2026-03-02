"""
Memori Enhanced - 自动记忆增强技能

在每次对话时自动检索相关知识并注入到上下文中。
"""
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# 添加技能目录到 Python 路径
skills_dir = Path(__file__).parent.parent.parent / "skills"
if str(skills_dir) not in sys.path:
    sys.path.insert(0, str(skills_dir))

from memori_integration import search_memori, get_memori_stats


# 关键词列表（用于检测是否需要检索记忆）
KEYWORDS = [
    # Linux 内核相关
    "linux", "kernel", "内核",
    # Rust 相关
    "rust", "c2rust", "c to rust", "迁移",
    # FFI 相关
    "ffi", "bindgen", "cbindgen", "foreign function interface",
    "类型绑定", "类型转换",
    # 并发相关
    "spinlock", "mutex", "锁", "并发", "concurrency",
    # 代码相关
    "unsafe", "生命周期", "lifetime", "内存安全",
    # 架构相关
    "架构", "模块", "依赖", "构建",
    # 错误模式
    "错误", "问题", "冲突", "失败",
]


def should_enhance(query: str) -> bool:
    """
    判断是否需要增强记忆

    Args:
        query: 用户查询

    Returns:
        是否需要检索相关知识
    """
    query_lower = query.lower()

    # 检查是否包含关键词
    for keyword in KEYWORDS:
        if keyword.lower() in query_lower:
            return True

    return False


def extract_keywords(query: str) -> List[str]:
    """
    从查询中提取关键词用于检索

    Args:
        query: 用户查询

    Returns:
        关键词列表
    """
    # 简单的关键词提取：匹配预定义列表
    query_lower = query.lower()
    found_keywords = []

    for keyword in KEYWORDS:
        if keyword.lower() in query_lower:
            found_keywords.append(keyword)

    # 如果没有找到预定义关键词，使用分词（简单版）
    if not found_keywords:
        # 移除标点符号，分割成单词
        words = re.findall(r'\w+', query_lower)
        # 过滤掉常用停用词
        stopwords = {'的', '是', '在', '了', '和', '与', '或', '但', '如果', '那么'}
        found_keywords = [w for w in words if len(w) > 2 and w not in stopwords]

    return found_keywords[:5]  # 最多返回 5 个关键词


def format_memori_context(results: List[Dict[str, Any]]) -> str:
    """
    格式化 Memori 检索结果为上下文文本

    Args:
        results: search_memori() 返回的结果列表

    Returns:
        格式化的上下文文本
    """
    if not results:
        return ""

    context_parts = []
    context_parts.append("## 相关专业知识 (来自 Memori 知识库)")
    context_parts.append("")
    context_parts.append("> 以下知识来自 Linux 内核 C2Rust 迁移专业知识库。")
    context_parts.append("")

    for i, result in enumerate(results, 1):
        context_parts.append(f"### 知识条目 {i}")
        context_parts.append(result['fact'])
        context_parts.append("")

    return "\n".join(context_parts)


def enhance_query(query: str, limit: int = 3) -> Optional[str]:
    """
    增强查询：检索相关知识并格式化为上下文

    Args:
        query: 用户查询
        limit: 检索的最大条目数

    Returns:
        增强的上下文文本，如果不需要增强则返回 None
    """
    # 1. 检查是否需要增强
    if not should_enhance(query):
        return None

    # 2. 提取关键词
    keywords = extract_keywords(query)
    if not keywords:
        # 使用原始查询
        search_query = query
    else:
        search_query = " ".join(keywords)

    # 3. 检索相关知识
    results = search_memori(search_query, limit=limit)

    if not results:
        return None

    # 4. 格式化为上下文
    context = format_memori_context(results)

    return context


def build_enhanced_prompt(query: str, original_prompt: str = "") -> str:
    """
    构建增强后的提示

    Args:
        query: 用户查询
        original_prompt: 原始系统提示（可选）

    Returns:
        增强后的完整提示
    """
    # 获取相关知识
    context = enhance_query(query)

    if not context:
        # 不需要增强，返回原始提示
        return f"{original_prompt}\n\n用户: {query}" if original_prompt else query

    # 构建增强提示
    enhanced = f"""{context}

{original_prompt}

用户问题: {query}

请基于以上专业知识，结合你的能力，详细回答用户的问题。
"""

    return enhanced


# 便捷函数
def quick_enhance(query: str) -> str:
    """
    快速增强查询（返回完整提示）

    Args:
        query: 用户查询

    Returns:
        增强后的提示
    """
    return build_enhanced_prompt(query)


if __name__ == "__main__":
    # 测试代码
    print("=== Memori Enhanced 测试 ===\n")

    # 显示数据库状态
    stats = get_memori_stats()
    print(f"数据库: {stats.get('path', 'N/A')}")
    print(f"知识条目: {stats.get('fact_count', 0)} 条\n")

    # 测试查询
    test_queries = [
        "FFI 绑定中如何处理 spinlock 类型冲突？",
        "Linux 内核 Rust 迁移中的 unsafe 使用原则",
        "今天天气怎么样",  # 不应该触发
    ]

    for query in test_queries:
        print(f"\n查询: {query}")
        print("-" * 60)

        # 检查是否需要增强
        if should_enhance(query):
            print("✅ 需要记忆增强")

            # 获取上下文
            context = enhance_query(query, limit=2)
            if context:
                print("检索到的知识:")
                print(context[:300] + "..." if len(context) > 300 else context)
            else:
                print("未检索到相关知识")
        else:
            print("❌ 不需要记忆增强（非技术问题）")
