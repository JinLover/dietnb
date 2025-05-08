# `dietnb` (v0.1.3) — The "Notebook Bloat" Instant Diet Pill

[![PyPI version](https://badge.fury.io/py/dietnb.svg)](https://badge.fury.io/py/dietnb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`dietnb` addresses the issue of large `.ipynb` file sizes caused by `matplotlib` figures being embedded as Base64 data. By saving plots as external PNG files and embedding only image links, `dietnb` keeps your notebooks lightweight and improves manageability.

---

## Key Features

*   **Minimized Notebook Size:** Significantly reduces `.ipynb` file bulk by storing `matplotlib` figures as external PNG files.
*   **Automatic Image Folder Management:** Creates and manages image storage directories (e.g., `[NotebookFileName]_dietnb_imgs`) relative to the notebook's location. (Applies when path detection is successful, e.g., in VS Code; defaults to `dietnb_imgs` in the current working directory if detection fails.)
*   **Automatic Image Updates:** When a notebook cell is re-executed, image files generated from its previous run are automatically deleted, ensuring only the latest output is retained.
*   **Image Cleanup Function:** The `dietnb.clean_unused()` function allows easy removal of unreferenced image files from the current session.
*   **Simple Auto-Activation:** The `dietnb install` command configures `dietnb` to activate automatically when IPython and Jupyter environments start.

---

## Installation and Activation

**1. Install the `dietnb` package**

Execute the following command in your terminal:
```bash
pip install dietnb
```

**2. Choose an Activation Method**

   **A. Automatic Activation (Recommended)**
   Run the following command in your terminal once:
   ```bash
   dietnb install
   ```
   This creates a startup script (`00-dietnb.py`) in your IPython profile directory.
   After restarting your Jupyter kernel, `dietnb` will be activated automatically. Images will be saved to a folder based on the notebook's path or to the default `dietnb_imgs` directory.

   To **disable** automatic activation later, run:
   ```bash
   dietnb uninstall
   ```
   This removes the startup script.

   **B. Manual Activation (Per Notebook)**
   If you prefer to use `dietnb` only for specific notebooks or do not want automatic activation, add the following code at the top of your notebook to activate it manually:
   ```python
   import dietnb
   dietnb.activate()
   ```

---

## Example Usage

With `dietnb` active, use your `matplotlib` code as usual.

```python
import matplotlib.pyplot as plt
import numpy as np

# Create a plot
x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x), label='sin(x)')
plt.plot(x, np.cos(x), label='cos(x)')
plt.title("Trigonometric Functions")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()

plt.show() # On show(), the image is saved to a file, and a link is displayed in the notebook.
```
Generated images can be found in the `[NotebookFileName]_dietnb_imgs` folder alongside your notebook, or in the `dietnb_imgs` folder.

---

## Cleaning Unused Image Files

To remove image files that are no longer in use, execute the following function in a notebook cell:

```python
import dietnb
dietnb.clean_unused()
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---
[한국어 README (Korean README)](README_ko.md) 