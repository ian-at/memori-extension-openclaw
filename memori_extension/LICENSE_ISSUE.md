# 解决 "Remove non-text files: LICENSE" 问题

## 问题分析

ClawHub 提示 "Remove non-text files: LICENSE"，说明：

1. ClawHub 可能检测到 LICENSE 文件为"非文本"
2. 或者 ClawHub 不允许上传 LICENSE 文件
3. 或者文件格式有问题

## 🔍 检查结果

### 文件类型
```bash
file LICENSE
```
应该显示：`ASCII text` 或 `UTF-8 Unicode text`

### 文件内容
LICENSE 文件是 **纯文本的 Apache 2.0 许可证**，绝对是文本文件。

## 💡 解决方案

### 方案 1: 在 .gitignore 中忽略 LICENSE（不推荐）

虽然不推荐，但如果 ClawHub 真的不允许 LICENSE 文件：

```bash
# 添加到 .gitignore
echo "LICENSE" >> .gitignore

# 提交更改
git add .gitignore
git commit -m "Add LICENSE to gitignore"
git push
```

**然后重新提交到 ClawHub**

### 方案 2: 将 LICENSE 内容移到 README.md（推荐）

如果 ClawHub 不接受单独的 LICENSE 文件，将许可证内容放在 README.md 中：

```bash
# 将 LICENSE 内容追加到 README.md
cat LICENSE >> README.md

# 提交
git add README.md
git rm LICENSE
git commit -m "Move LICENSE content to README.md"
git push
```

### 方案 3: 重命名为 LICENSE.txt 或 LICENSE.md

有些系统更接受这些扩展名：

```bash
git mv LICENSE LICENSE.md
git commit -m "Rename LICENSE to LICENSE.md"
git push
```

### 方案 4: 在 SKILL.md 中声明许可证（推荐）

在 SKILL.md 的 metadata 中明确声明许可证，这样即使没有单独的 LICENSE 文件也可以：

```yaml
---
metadata: {
  "license": "Apache-2.0",
  ...
}
---
```

然后在文档末尾包含许可证摘要。

### 方案 5: 检查是否是 ClawHub 的限制（最可能）

**ClawHub 可能：**
- 只接受源代码文件
- 不接受单独的 LICENSE 文件
- 要求许可证信息在 SKILL.md 或 README.md 中声明

**这是正常的！** 许多平台都有类似限制。

## ✅ 推荐做法

### 最简单的解决方案

**1. 删除 LICENSE 文件（只在技能目录中）**

```bash
cd /home/yishuqi/.openclaw/workspace/skills/memori_extension
git rm LICENSE
git commit -m "Remove LICENSE file (ClawHub restriction)"
git push
```

**2. 在 README.md 中声明许可证**

在 README.md 顶部或底部添加：

```markdown
# Memori Zhipu Skill

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

This skill uses the Memori Python library (Apache License 2.0).
See: https://github.com/MemoriLabs/Memori
```

**3. 重新提交到 ClawHub**

这样既符合 ClawHub 的要求，又保留了许可证信息。

## 📝 更新后的文件结构

```
memori_extension/
├── __init__.py              # 技能入口
├── memori_extension.py      # 核心实现
├── SKILL.md                 # 技能文档（包含许可证声明）
├── README.md                # 说明文档（包含许可证全文）
└── ...                      # 其他文件
```

## 🎯 快速修复步骤

```bash
# 1. 进入技能目录
cd /home/yishuqi/.openclaw/workspace/skills/memori_extension

# 2. 删除 LICENSE 文件
git rm LICENSE

# 3. 更新 README.md（添加许可证信息）
# 手动编辑 README.md，添加 Apache 2.0 许可证全文

# 4. 提交
git add README.md
git commit -m "Remove LICENSE, add license to README.md"

# 5. 推送到 GitHub
git push

# 6. 重新提交到 ClawHub
```

## ⚠️ 注意

- **GitHub 仓库**: 可以保留 LICENSE 文件（推荐）
- **ClawHub 提交**: 可能需要移除 LICENSE 文件
- **许可证信息**: 必须在 README.md 或 SKILL.md 中声明

## 📚 许可证要求

即使没有单独的 LICENSE 文件，你也需要：

1. ✅ 在 README.md 中包含许可证全文
2. ✅ 在 SKILL.md metadata 中声明许可证
3. ✅ 包含 Memori 库的归属声明
4. ✅ 遵守 Apache 2.0 的所有要求

## 🔗 参考资源

- Apache 2.0 许可证全文: http://www.apache.org/licenses/LICENSE-2.0
- ClawHub 提交要求: https://docs.clawhub.com/submit

---

**总结**: ClawHub 不接受单独的 LICENSE 文件是正常的。将许可证信息放在 README.md 中即可。
