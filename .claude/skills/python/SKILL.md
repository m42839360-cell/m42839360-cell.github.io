# Python Skill - UV-Based Execution

You are helping the user work with Python code. **CRITICAL**: All Python execution MUST use `uv`. NEVER run `python` directly.

## UV Execution Rules

### For Single Scripts (Standalone Files)

1. **Always use the UV shebang with PEP 723 inline dependencies:**
   ```python
   #!/usr/bin/env -S uv run --script
   # /// script
   # dependencies = [
   #   "requests>=2.31.0",
   #   "pandas>=2.0.0",
   # ]
   # ///

   import requests
   import pandas as pd

   # Your code here
   ```

2. **Make the script executable and run it:**
   ```bash
   chmod +x script.py
   ./script.py
   ```

3. **Or run directly with uv:**
   ```bash
   uv run script.py
   ```

### For Projects (Multiple Files/Packages)

1. **Initialize a full uv project:**
   ```bash
   uv init
   ```

2. **Add dependencies:**
   ```bash
   uv add package-name
   ```

3. **Run Python code:**
   ```bash
   uv run python script.py
   # or
   uv run module_name
   ```

4. **Sync dependencies:**
   ```bash
   uv sync
   ```

## Decision Tree

When the user asks to run Python code:

1. **Is this a single standalone script?**
   - YES → Use UV shebang with PEP 723 dependencies
   - NO → Continue to step 2

2. **Does a pyproject.toml exist?**
   - YES → Use `uv run` with the existing project
   - NO → Initialize with `uv init` and set up the project

3. **Are new dependencies needed?**
   - YES → Add them with `uv add package-name`
   - NO → Just use `uv run`

## Examples

### Example 1: Simple Script with Dependencies
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "httpx>=0.27.0",
# ]
# ///

import httpx

response = httpx.get("https://api.example.com")
print(response.json())
```

### Example 2: Data Analysis Script
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "pandas>=2.0.0",
#   "matplotlib>=3.7.0",
#   "seaborn>=0.13.0",
# ]
# requires-python = ">=3.11"
# ///

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Analysis code here
```

### Example 3: Project Initialization
```bash
# Initialize project
uv init my_project
cd my_project

# Add dependencies
uv add fastapi uvicorn

# Run the application
uv run uvicorn main:app
```

## Code Formatting

**ALWAYS run `uv format` when finishing up** to ensure code is properly formatted:

```bash
# Format all Python files in the project
uv format

# Format specific file(s)
uv format script.py
uv format src/
```

Run formatting:
- After creating or modifying Python files
- Before running the final version of scripts
- As the final step before completing the task

## Important Notes

- **NEVER** use `python` command directly
- **NEVER** use `pip` for package installation
- **ALWAYS** check if it's a single script or a project first
- **ALWAYS** run `uv format` when finishing up to format the code
- For single scripts, include ALL dependencies in the PEP 723 header
- Use semantic versioning for dependencies (e.g., `>=2.0.0`, `~=1.5.0`)
- When creating new Python files, default to the UV shebang approach unless it's clearly part of a larger project

## Your Task

Proceed with the user's Python-related request, strictly following the UV execution rules above. Remember to run `uv format` as your final step.
