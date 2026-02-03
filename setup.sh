#!/bin/bash
# 快速设置脚本

echo "🦞 Skill Executor - 测试环境设置"
echo "=================================="
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "当前 Python 版本: $python_version"

# 安装测试依赖
echo ""
echo "安装测试依赖..."
pip install pytest pytest-cov pytest-mock

echo ""
echo "✅ 设置完成！"
echo ""
echo "运行测试:"
echo "  make test          # 运行所有测试"
echo "  make test-cov      # 查看测试覆盖率"
echo ""
echo "或直接使用 pytest:"
echo "  pytest -v"
