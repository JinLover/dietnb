# `dietnb` (v0.1.2)

[![PyPI version](https://badge.fury.io/py/dietnb.svg)](https://badge.fury.io/py/dietnb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`dietnb` automatically saves `matplotlib` figures as local PNG files and embeds `<img>` links in Jupyter notebooks. This prevents base64 image embedding, significantly reducing `.ipynb` file sizes.

---

## Key Features

*   **Reduces Notebook Size:** Stores images externally in a `{notebook_filename}_dietnb_imgs/` directory next to the notebook, keeping `.ipynb` files small.
*   **Automatic Cleanup:** Deletes images from a cell's previous execution when the cell is re-run.
*   **Manual Cleanup:** Provides `dietnb.clean_unused()` to remove image files no longer referenced by the current kernel session.

## Installation

```bash
pip install dietnb
```

## Usage

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

To remove image files no longer referenced by the current kernel:

```python
import dietnb
dietnb.clean_unused()
```

## License

MIT License. See [LICENSE](LICENSE) for details.

---
[한국어 README (Korean README)](README_ko.md) 