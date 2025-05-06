# `dietnb` (v0.1.1)

[![PyPI version](https://badge.fury.io/py/dietnb.svg)](https://badge.fury.io/py/dietnb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`dietnb` automatically saves `matplotlib` figures as external PNG files and embeds them as `<img>` links in Jupyter notebooks. This significantly reduces `.ipynb` file sizes by preventing base64 image embedding.

---

## Key Features

*   **Reduces Notebook Size:** Stores images externally, keeping `.ipynb` files small.
*   **Automatic Operation:** Works in the background after installation and a one-time setup.
*   **Cell-Specific Naming:** Images are named based on cell ID and an index for multiple figures per cell.
*   **Automatic Cleanup:** Deletes a cell's previous images upon re-execution.
*   **Cache Busting:** Uses a version query in image links for reliable updates.
*   **Manual Cleanup:** `dietnb.clean_unused()` function to remove orphaned images.

## Installation

```bash
pip install dietnb
```

## Usage

**1. Automatic Activation (Recommended)**

After installing, run this in your terminal (with your virtual environment activated):

```bash
dietnb install
```
Then, **restart your Jupyter kernel(s)**. `dietnb` will be active in all new sessions.

**2. Manual Activation (Per Notebook)**

Add one of the following to the beginning of your notebook:

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
plt.show() # Saved to dietnb_imgs/your_notebook_name_figures/ and linked
```

Figures will be saved in a `dietnb_imgs` subdirectory (by default) next to your notebook.

## Cleaning Unused Images

To remove image files no longer referenced by the kernel:

```python
import dietnb
dietnb.clean_unused()
```

## License

MIT License. See [LICENSE](LICENSE) for details.

---
[한국어 README (Korean README)](README_ko.md) 