问题在于您在 subprocess 中设置了 UTF-8 编码，但脚本内部使用了 `os.popen()`，而 `os.popen()` 不会继承 subprocess 的编码设置，仍然使用系统默认编码（Windows 上通常是 GBK）。

## 解决方案

有几种方法可以解决这个问题：

### 方案 1：在脚本内部设置环境变量（推荐）

在生成的脚本开头添加编码设置，确保 `os.popen()` 也使用 UTF-8：

```python
#!/usr/bin/env python3
"""
Generated script with proper encoding handling
"""

import os
import sys

# 🔥 Windows 编码修复 - 在脚本开头设置
if sys.platform == "win32":
    # 设置标准输出/输入/错误流为 UTF-8
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
    if sys.stdin.encoding != 'utf-8':
        sys.stdin.reconfigure(encoding='utf-8')

# 现在可以安全使用 os.popen()
result = os.popen("some_command").read()
print(result)
```


### 方案 2：在 Skill Creation Workflow 中添加模板指导

更新 `prompts/skill_creation_workflow.md`，在脚本模板部分添加编码处理：

```markdown
#### **📝 Standard Script Template for Graph Database Skills**

**Use this template for all graph database query scripts:**
```
python
#!/usr/bin/env python3
"""
[Script Description]

Usage:
    python script_name.py [arguments]

Environment Variables Required:
    GRAPH_DB_BASE_URL - Graph database API endpoint (auto-provided)
    GRAPH_DB_TIMEOUT  - Request timeout in seconds (auto-provided)
"""

import os
import sys
import json
from connectors import GraphConnector

# 🔥 Windows 编码修复 - CRITICAL for os.popen() and print()
if sys.platform == "win32":
    # 确保所有输出都使用 UTF-8
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

def get_graph_connector():
    """Get configured GraphConnector instance
    
    Reads configuration from environment variables that are
    automatically injected by the skill executor.
    """
    base_url = os.getenv("GRAPH_DB_BASE_URL")
    if not base_url:
        print("Error: GRAPH_DB_BASE_URL not set", file=sys.stderr)
        sys.exit(1)
    
    timeout = int(os.getenv("GRAPH_DB_TIMEOUT", "30"))
    
    return GraphConnector(base_url=base_url, timeout=timeout)

def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <argument>", file=sys.stderr)
        sys.exit(1)
    
    user_input = sys.argv[1]
    
    try:
        # Get connector with auto-injected config
        connector = get_graph_connector()
        
        # Perform query
        results = connector.property_filter(
            element_class="YourEntityType",
            element_type="NODE",
            filter_dict={"propertyName": f"= '{user_input}'"},
            get_all_properties=True
        )
        
        if not results:
            print(f"No results found for: {user_input}")
            sys.exit(0)
        
        # Output results
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```
**⚠️ IMPORTANT - Encoding Handling:**

When your script uses `os.popen()`, `subprocess`, or file I/O:

1. **Always add encoding fix at the top** (shown above)
2. **Use `encoding='utf-8'` for file operations:**
   ```python
   with open(file_path, 'r', encoding='utf-8') as f:
       content = f.read()
   ```
3. **Use `ensure_ascii=False` for JSON output:**
   ```python
   json.dumps(data, ensure_ascii=False, indent=2)
   ```
4. **Avoid `os.popen()` if possible, use `subprocess.run()` instead:**
   ```python
   # ❌ Bad - no encoding control
   result = os.popen("command").read()
   
   # ✅ Good - explicit encoding
   result = subprocess.run(
       ["command"],
       capture_output=True,
       text=True,
       encoding='utf-8',
       errors='replace'
   ).stdout
   ```
```


### 方案 3：在环境变量中设置 Python UTF-8 模式（已有）

您已经在 `models/skill.py` 中设置了：

```python
if sys.platform == "win32":
    run_env["PYTHONIOENCODING"] = "utf-8"
    run_env["PYTHONUTF8"] = "1"
```


但这可能不够，因为 `os.popen()` 在某些情况下不会遵守这些环境变量。

### 方案 4：禁止生成的脚本使用 `os.popen()`（最安全）

在 prompt 中明确禁止使用 `os.popen()`，推荐使用 `subprocess.run()`：

```markdown
#### **❌ Common Mistakes to Avoid:**

**Mistake 4: Using os.popen() instead of subprocess.run()**
```
python
# ❌ WRONG - os.popen() has encoding issues on Windows
import os
result = os.popen("dir").read()
```
✅ **Correct:**
```
python
# ✅ CORRECT - subprocess.run() with explicit encoding
import subprocess
result = subprocess.run(
    ["cmd", "/c", "dir"],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'  # Replace invalid chars instead of crashing
).stdout
```
**Why?**
- `os.popen()` uses system default encoding (GBK on Windows)
- `subprocess.run()` allows explicit encoding control
- `errors='replace'` prevents UnicodeDecodeError
```


### 方案 5：捕获并处理 UnicodeDecodeError

如果脚本确实需要使用 `os.popen()`，添加错误处理：

```python
import os
import sys

def safe_popen(command: str) -> str:
    """Safely execute command with proper encoding handling"""
    try:
        if sys.platform == "win32":
            # Windows: try UTF-8 first, fallback to GBK
            try:
                return os.popen(command).read().encode('latin1').decode('utf-8')
            except UnicodeDecodeError:
                return os.popen(command).read().encode('latin1').decode('gbk')
        else:
            # Unix/Linux: should be UTF-8 by default
            return os.popen(command).read()
    except Exception as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        return ""

# Usage
result = safe_popen("dir")
print(result)
```


## 推荐的综合方案

结合方案 1 和方案 4，在 Skill Creation Workflow 中：

1. **添加标准脚本模板**，包含 Windows 编码修复
2. **推荐使用 `subprocess.run()` 而不是 `os.popen()`**
3. **如果必须使用 `os.popen()`，提供安全包装函数**

这样生成的脚本就能在 Windows 上正确处理中文和其他 Unicode 字符了！