.PHONY: help test test-cov test-all clean lint install-dev

help: ## 显示帮助信息
	@echo "可用的命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-dev: ## 安装开发依赖
	pip install -r requirements-test.txt
	pip install -e .

test: ## 运行所有测试
	pytest -v

test-cov: ## 运行测试并显示覆盖率
	pytest --cov=. --cov-report=term-missing

test-html: ## 生成 HTML 覆盖率报告
	pytest --cov=. --cov-report=html
	@echo "报告已生成到 htmlcov/index.html"

test-unit: ## 只运行单元测试
	pytest tests/ -v

test-models: ## 测试 models 层
	pytest tests/models/ -v

test-loaders: ## 测试 loaders 层
	pytest tests/loaders/ -v

test-llm: ## 测试 llm 层
	pytest tests/llm/ -v

test-tools: ## 测试 tools 层
	pytest tests/tools/ -v

test-executor: ## 测试 executor 层
	pytest tests/executor/ -v

clean: ## 清理测试生成的文件
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint: ## 运行代码检查
	pyflakes .
	pycodestyle --max-line-length=100 .
