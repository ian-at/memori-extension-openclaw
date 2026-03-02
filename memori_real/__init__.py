"""
真正的 Memori - OpenClaw 集成层

在 OpenClaw Gateway 和 LLM 之间插入 Memori 记忆层
"""
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from memori_core import RealMemori, augment_and_query, Message, Memory

# 全局 Memori 实例
_memori_instance = None


def get_memori():
    """获取或创建全局 Memori 实例"""
    global _memori_instance
    if _memori_instance is None:
        _memori_instance = RealMemori()
    return _memori_instance


def should_use_memori(query: str) -> bool:
    """
    判断是否应该使用 Memori 增强检测关键词

    Args:
        query: 用户查询

    Returns:
        是否使用 Memori
    """
    # 技术关键词列表
    keywords = [
        "FFI", "bindgen", "spinlock", "mutex", "unsafe",
        "Rust", "Linux", "kernel", "内核", "迁移",
        "类型", "转换", "内存", "并发", "锁",
        "生命周期", "cbindgen", "C 语言"
    ]

    query_lower = query.lower()

    # 检查是否包含关键词
    for keyword in keywords:
        if keyword.lower() in query_lower:
            return True

    return False


def enhance_with_memori(query: str) -> str:
    """
    使用 Memori 增强查询

    这是 OpenClaw 调用的主函数

    Args:
        query: 用户查询

    Returns:
        增强后的提示（如果不需要增强则返回 None）
    """
    # 1. 检查是否需要增强
    if not should_use_memori(query):
        return None

    # 2. 获取 Memori 实例
    memori = get_memori()

    # 3. 增强查询
    context = memori.augment_query(query, limit=3)

    # 4. 返回增强提示
    if context.retrieved_memories:
        return context.enhanced_prompt
    else:
        return None


# OpenClaw 技能接口
def memori_enhance(query: str) -> str:
    """
    技能接口：增强查询

    在 OpenClaw 系统提示中调用此函数

    使用示例：
    ```
    用户问题: {query}

    {memori_enhance(query)}
    ```
    """
    return enhance_with_memori(query) or ""


if __name__ == "__main__":
    # 测试
    print("=== OpenClaw Memori 集成测试 ===\n")

    test_queries = [
        "FFI 绑定中如何处理 spinlock 类型冲突？",
        "今天天气怎么样",
        "Linux 内核 Rust 迁移的最佳实践"
    ]

    for query in test_queries:
        print(f"查询: {query}")
        print("-" * 60)

        if should_use_memori(query):
            print("✅ 使用 Memori 增强")
            enhanced = enhance_with_memori(query)
            if enhanced:
                print(f"增强后长度: {len(enhanced)} 字符")
                print(f"预览:\n{enhanced[:300]}...")
            else:
                print("⚠️  未检索到相关记忆")
        else:
            print("❌ 不使用 Memori（非技术问题）")

        print()
