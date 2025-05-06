# **`dietnb` (v0.1.0) — Instant Relief for "Notebook Obesity"**

> **The Problem**
> * `matplotlib` Figures saved as Base64 in `.ipynb` → Notebook size (MB) ↗︎↗︎
> * Cached/accumulated Figures consume memory
> * Annoying to run `plt.close`, `nbstripout` every time

**`dietnb`** automatically applies a **"Figures on disk, links in notebook"** design, keeping your `.ipynb` files almost **0 bytes** with just installation.

---

## 0. Core Rules (Design Principles) - Implemented

| # | Rule                                      | Implementation Point                               |
|---|-------------------------------------------|----------------------------------------------------|
| 1 | **Zero image bytes inside ipynb**         | `Figure._repr_png_ = None` (Block PNG embedding)   |
| 2 | **Unique prefix per cell**                | `cellId` (+ SHA-1 fallback)                        |
| 3 | **Rerun cell → Delete all previous PNGs** | `_state[key] != exec_id` check                     |
| 4 | **Multiple figures in one cell → `_1,_2,…`** | Index by `glob(f"{key}_*.png")` count             |
| 5 | **Browser cache invalidation**            | `<img …?v=exec_id>`                               |
| 6 | **Apply from the first Figure**           | Direct override of `_repr_html_`                   |
| 7 | **Prevent backend re-registration issues**| Re-inject patch on `post_run_cell`                 |

---

## 1. Quick Start

```bash
pip install dietnb                 # ➊ Install
dietnb install                     # ➋ Register automatic startup script
```

*After running `dietnb install` and restarting the kernel, it applies automatically to any notebook.*

> **Manual Mode** — If you don't want to use or failed with automatic startup setup:
> Run `import dietnb; dietnb.activate()` **or** `%load_ext dietnb` at the beginning of your notebook.

---

## 2. Additional Feature — "Clean Images" Button

| UI                                     | Function                                                  |
|----------------------------------------|-----------------------------------------------------------|
| 🗑 Toolbar Button                      | Bulk delete PNGs **not loaded in the current kernel** (`dietnb_js` required, **Not Implemented**) |
| Command Palette `DietNB: Clean Images` | Same function (`dietnb_js` required, **Not Implemented**) |
| **Python Function**                    | Call `dietnb.clean_unused()` (**Implemented**)            |

*Currently, you can use this feature by calling `dietnb.clean_unused()` directly in a notebook cell.*

---

## 3. Package Structure (Implemented)

```
dietnb/
├─ dietnb
│  ├─ __init__.py         # Public API: activate(), deactivate(), clean_unused()
│  ├─ _core.py            # Core logic for saving/linking Figures, state management
│  ├─ _startup.py         # IPython startup script content copied by `dietnb install`
│  ├─ _ipython.py         # Implements `%load_ext dietnb`
│  └─ _cli.py             # Logic for `dietnb install` command (main function)
├─ dietnb_js/             # Lab/VSC UI (Optional, **Not Implemented**)
├─ tests/                 # Automated tests (pytest, **Basic setup only**)
├─ README.md              # This file (English)
├─ README_ko.md           # Korean version of README
└─ pyproject.toml
```

### `_core.activate()` Main Flow (Implemented)

```python
def activate(folder="dietnb_imgs"):
    ip = get_ipython()                            # ①
    ip.display_formatter.formatters['image/png'].enabled = False # Disable PNG formatter
    Figure._repr_png_  = lambda self: None        # ② Completely block PNG embedding
    Figure._repr_html_ = lambda fig: _save_figure_and_get_html(fig, ip) # ③ Connect HTML generation logic
    # ④ Register handler for post-cell cleanup and re-patching (modified to accept IPython event args)
    ip.events.register('post_run_cell', _post_cell_cleanup_and_repatch_handler)
```

---

## 4. `pyproject.toml` Core (Implemented)

```toml
[project]
name            = "dietnb"
version         = "0.1.0"
description     = "Save matplotlib figures as external files and link them, keeping notebooks tiny."
readme          = "README.md" # Points to this English README
license         = {text = "MIT"}
authors         = [{name = "JinLover"}]
requires-python = ">=3.8"
dependencies    = ["ipython>=8", "matplotlib>=3.5"]

[project.scripts]
dietnb = "dietnb._cli:main"         # Creates `dietnb` command -> links to _cli.main

[tool.setuptools.packages.find]
# Specify where to find package code (inside 'dietnb' directory under project root)
where = ["dietnb"]

[project.optional-dependencies]
# Dependencies for development and testing (`pip install -e '.[dev]'`)
dev = [
    "pytest>=7.0",
    "pytest-mock>=3.10"
]
```

---

## 5. Deployment (Completed)

```bash
python -m pip install --upgrade build twine  # ➊ Install build tools (Completed)
python -m build                            # ➋ Create dist/ directory (Completed)
twine upload dist/*                        # ➌ Upload to PyPI (Completed)
```

---

## 6. Usage Example (Confirmed Working)

```python
# After running `dietnb install` and restarting the kernel, or after manual activation:
import numpy as np
import matplotlib.pyplot as plt

for i in range(3):
    plt.plot(np.linspace(0, 100), np.sin(np.linspace(0, 10) + i))
    plt.show() # Automatically saves to dietnb_imgs/ folder and outputs a link
```

*   ipynb size increase ≈ 120 bytes
*   `dietnb_imgs/<hash>_{1,2,3}.png` created
*   Calling `dietnb.clean_unused()` after running other cells can clean up images from previous cells

---

## 7. Current Status & Roadmap

### Current Status (as of v0.1.0) - PyPI Deployment Completed
*   **Core Functionality Implemented:** External saving of Matplotlib figures and linking works correctly.
*   **Installation & Auto-activation Implemented:** Installation via `pip install dietnb` and auto-start script registration via `dietnb install` completed.
*   **Manual Activation Implemented:** `%load_ext dietnb` and `dietnb.activate()` work.
*   **Image Cleanup Functionality Implemented:** `dietnb.clean_unused()` function completed.
*   **Basic Package Structure Completed:** Packaging based on `pyproject.toml` and CLI setup completed.
*   **License File Added:** `LICENSE` (MIT) file added.
*   **Source Code Pushed to GitHub:** Source code published at `https://github.com/JinLover/dietnb`.
*   **Package Built:** Distribution files created in `dist/` folder.
*   **PyPI Deployment Completed:** v0.1.0 registered on PyPI ([https://pypi.org/project/dietnb/0.1.0/](https://pypi.org/project/dietnb/0.1.0/))

### Not Implemented & Next Steps
*   **Update `pyproject.toml` license format:** Resolve `setuptools` warning about `project.license` table format.
*   **Automated Tests:** `tests/` directory and `pytest` setup exist, but detailed test cases need to be written.
*   **JupyterLab/VS Code UI:** `dietnb_js` needs implementation (Toolbar button, Command Palette integration).
*   **Roadmap v0.2 and beyond:** nbconvert plugin, Classic Notebook support, JupyterLite compatibility, etc.

---

## 8. License / Credits

*MIT.*
Idea & Initial Code: **JinLover × ChatGPT**
Current Development: **Cursor AI (Gemini)**
Issues / PRs welcome.

---
[한국어 README (Korean README)](README_ko.md) 