# Jupyter Notebook Creation Guide

## Overview

When creating Jupyter notebooks (.ipynb files) for this project, you MUST use a Python script generator approach rather than creating the notebook JSON directly.

## Why Use a Script Generator?

Jupyter notebooks are JSON files with a complex nested structure. Creating them directly leads to:
- Syntax errors from improperly escaped strings
- Malformed JSON structure
- Difficulty managing large cell content
- Hard-to-debug issues

## The Correct Approach

### Step 1: Create a Python Script Generator

Create a Python script (e.g., `create_<notebook_name>.py`) that:
1. Builds the notebook structure programmatically
2. Uses proper Python string handling (no manual JSON escaping needed)
3. Writes the final JSON to a .ipynb file

### Step 2: Script Structure

```python
#!/usr/bin/env python3
"""
Script to create the <notebook_name>.ipynb notebook
"""

import json

def create_notebook():
    notebook = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    cells = [
        # Markdown cell
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Notebook Title\n",
                "\n",
                "Description here."
            ]
        },
        
        # Code cell
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "import numpy as np\n",
                "\n",
                "print('Hello World')"
            ]
        }
    ]
    
    notebook['cells'] = cells
    
    # Write to file
    with open('notebook_name.ipynb', 'w') as f:
        json.dump(notebook, f, indent=2)
    
    print(f"✓ Created notebook_name.ipynb with {len(cells)} cells")

if __name__ == "__main__":
    create_notebook()
```

### Step 3: Run the Script

```bash
cd <notebook_directory>
python create_<notebook_name>.py
```

## Key Benefits

1. **No String Escaping**: Python handles all string escaping automatically
2. **Readable Code**: Cell content is written as normal Python strings
3. **Easy Debugging**: Syntax errors are caught by Python before JSON generation
4. **Maintainable**: Easy to modify and regenerate notebooks
5. **Version Control**: The generator script is easier to review in git than raw JSON

## Cell Structure Reference

### Markdown Cell
```python
{
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# Heading\n",
        "\n",
        "Paragraph text."
    ]
}
```

### Code Cell
```python
{
    "cell_type": "code",
    "execution_count": None,  # Use None for unexecuted cells
    "metadata": {},
    "outputs": [],
    "source": [
        "# Python code here\n",
        "import pandas as pd\n",
        "\n",
        "df = pd.DataFrame()"
    ]
}
```

## Important Notes

- **Always use `\n` for newlines** in the source strings (not `\\n`)
- **Set `execution_count` to `None`** for unexecuted notebooks
- **Use proper indentation** in the source strings to match how code should appear
- **Keep the generator script** in the same directory as the notebook for future updates
- **Test the notebook** after generation by opening it in Jupyter

## Example: Real-World Usage

See `forecasts/us_recession_2025/notebooks/create_indicator_analysis.py` for a complete example that:
- Creates a 24-cell notebook
- Includes complex data analysis code
- Handles multiple indicator visualizations
- Properly escapes all strings automatically

## When to Regenerate

Regenerate the notebook when you need to:
- Add new cells
- Modify existing cell content
- Fix bugs in the analysis code
- Update documentation

Simply modify the generator script and run it again. The notebook will be completely regenerated with your changes.
