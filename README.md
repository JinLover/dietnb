# `dietnb`

[![PyPI version](https://badge.fury.io/py/dietnb.svg)](https://badge.fury.io/py/dietnb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow?logo=buymeacoffee)](https://coff.ee/jinlover)

`dietnb` addresses the issue of large `.ipynb` file sizes caused by `matplotlib` figures being embedded as Base64 data. By saving plots as external PNG files and embedding only image links, `dietnb` keeps your notebooks lightweight and improves manageability.

---

## Key Features

*   **Minimized Notebook Size:** Significantly reduces `.ipynb` file bulk by storing `matplotlib` figures as external PNG files.
*   **Automatic Image Folder Management:** Creates and manages image storage directories (e.g., `[NotebookFileName]_dietnb_imgs`) relative to the notebook's location. When you move the notebook and the folder together, the `<img>` tags continue to work because only relative paths are stored. If detection fails, the default `dietnb_imgs` folder in the working directory is used.
*   **Automatic Image Updates:** Registers per-directory/per-cell execution counts to replace old PNGs when a cell reruns, preventing stale images from piling up.
*   **Image Cleanup Function:** The `dietnb.clean_unused()` function consults the execution registry to remove unreferenced image files from the active session.
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
Generated images can be found in the `[NotebookFileName]_dietnb_imgs` folder alongside your notebook (with relative links), or in the `dietnb_imgs` folder.

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