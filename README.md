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
2.  **Activate:**
    You have two main options:

    *   **Automatic Activation (Recommended):** Run `dietnb install` once in your terminal. After restarting your Jupyter kernel, `dietnb` will activate automatically in all sessions. It will try to save images to a notebook-specific folder (e.g., `MyNotebook_dietnb_imgs`) or fall back to `dietnb_imgs`.

    *   **Manual Activation (Per Notebook):** Add the following to the top of your notebook if you prefer to activate `dietnb` manually:
        ```python
        import dietnb
        dietnb.activate()
        ```

That's it! `matplotlib` figures will now be saved externally.

*(The `dietnb install` command handles automatic activation. Manual activation is an alternative.)*

## How it Works

(Simplified: remove detailed breakdown of activate() options, focus on the outcome)
`dietnb` patches `matplotlib.figure.Figure` when activated. When a figure is to be displayed:
1. It disables the default inline PNG embedding.
2. It saves the figure to a directory:
    - Tries to determine the current notebook's path (e.g., in VS Code via `__vsc_ipynb_file__`) and creates a folder like `[notebook_name]_dietnb_imgs` next to it.
    - If the notebook path cannot be found, it defaults to `dietnb_imgs` in the current working directory.
3. It generates an `<img>` HTML tag linking to the saved file, including a cache-busting query parameter.
4. When a cell is re-executed, `dietnb` cleans up old images from that cell's previous output in the determined folder.

## Cleaning Unused Images

To remove any image files from the relevant image directory (`dietnb_imgs` or `[notebook_name]_dietnb_imgs`) that no longer correspond to an active cell output in the current IPython session, call:

```python
import dietnb
dietnb.clean_unused()
```

## License

MIT License. See [LICENSE](LICENSE) for details.

---
[한국어 README (Korean README)](README_ko.md) 