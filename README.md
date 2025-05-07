# `dietnb` (v0.1.2)

[![PyPI version](https://badge.fury.io/py/dietnb.svg)](https://badge.fury.io/py/dietnb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`dietnb` automatically saves `matplotlib` figures as local PNG files and embeds `<img>` links in Jupyter notebooks. This prevents base64 image embedding, significantly reducing `.ipynb` file sizes.

---

## Key Features

*   **Reduces Notebook Size:** Stores images externally in a `{notebook_filename}_dietnb_imgs/` directory next to the notebook, keeping `.ipynb` files small.
*   **Automatic Cleanup:** Deletes images from a cell's previous execution when the cell is re-run.
*   **Manual Cleanup:** Provides `dietnb.clean_unused()` to remove image files no longer referenced by the current kernel session.

## Quick Start

1.  **Install:**
    ```bash
    pip install dietnb
    ```
2.  **Activate (Mandatory in each notebook):**
    Add **one** of the following lines at the beginning of your notebook:

    ```python
    # Option 1: Python call (default folder: 'dietnb_imgs' or auto-detected)
    import dietnb
    dietnb.activate() 

    # Option 1a: Python call (custom folder: 'MyProject_dietnb_imgs')
    # import dietnb
    # dietnb.activate(folder_prefix="MyProject")
    ```
    ```python
    # Option 2: IPython magic
    %load_ext dietnb
    ```

That\'s it! After activation, `matplotlib` figures generated via `plt.show()` or displayed at the end of a cell will be automatically saved to a folder and linked in the output. 
- By default, this folder is `dietnb_imgs` (relative to the notebook\'s execution directory) or a name derived from your notebook file if auto-detection is successful.
- If you use `dietnb.activate(folder_prefix="PREFIX")`, images will be saved to `PREFIX_dietnb_imgs`.

*(Note: The `dietnb install` command for automatic activation is disabled in this version.)*

## How it Works

**1. Automatic Activation (Recommended)**

After installation, run this command in your terminal (with your virtual environment activated):

```bash
dietnb install
```
Then, **restart your Jupyter kernel(s)**. `dietnb` will be active in all new sessions.

**2. Manual Activation (Per Notebook)**

Add one of the following to the top of your notebook:

```python
# Option A: Python code
import dietnb
dietnb.activate()
```

```python
# Option B: IPython magic
%load_ext dietnb
```

**Example:**

Once active, use `matplotlib` as usual:

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.title("Sine Wave")
plt.show() # Figure is saved locally, and a link is displayed in the notebook.
```

## Cleaning Unused Images

To remove images from a previous cell execution (or an old notebook session for a given prefix), you can call:

```python
import dietnb

# Clean for the default/auto-detected folder context
dietnb.clean_unused()

# Clean for a specific folder_prefix context
# dietnb.clean_unused(folder_prefix="MyProject")
```

This function will scan the relevant image directory (`dietnb_imgs`, `[notebook_name]_dietnb_imgs`, or `[prefix]_dietnb_imgs`) and delete any `.png` files that don\'t correspond to an active cell output in the current IPython session for that context.

## License

MIT License. See [LICENSE](LICENSE) for details.

---
[한국어 README (Korean README)](README_ko.md) 