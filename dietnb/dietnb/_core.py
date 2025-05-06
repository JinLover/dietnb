import hashlib
import logging
import warnings
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from IPython import get_ipython
from matplotlib.figure import Figure

# Global state
_state = {}  # Stores {cell_key: last_exec_count}
_active_folder = Path.cwd() / "dietnb_imgs" # Default folder, updated by activate()
_patch_applied = False

# Configure logging
logger = logging.getLogger(__name__)

def _get_cell_key(ip) -> str:
    """Generates a unique key for the current cell execution."""
    if not ip:
        # Fallback if IPython is not available
        return hashlib.sha1(str(plt.gcf().number).encode()).hexdigest()[:12]

    # Prefer cellId from metadata (JupyterLab >= 3, VS Code, etc.)
    meta = ip.parent_header.get("metadata", {})
    cell_id = meta.get("cellId") or meta.get("cell_id")

    if cell_id:
        return hashlib.sha1(cell_id.encode()).hexdigest()[:12]

    # Fallback to hashing the raw cell content (less reliable)
    try:
        raw_cell = ip.history_manager.input_hist_raw[-1]
        return hashlib.sha1(raw_cell.encode()).hexdigest()[:12]
    except (AttributeError, IndexError):
        # Fallback if history is not available or empty
        warnings.warn("Could not reliably determine cell identity. Using figure number.", stacklevel=2)
        return hashlib.sha1(str(plt.gcf().number).encode()).hexdigest()[:12]

def _save_figure_and_get_html(fig: Figure, ip, fmt="png", dpi=150) -> Optional[str]:
    """Saves the figure to a file and returns an HTML img tag."""
    global _state, _active_folder
    if not ip:
        logger.error("IPython kernel not found. Cannot save figure.")
        return None # Or raise an error

    key = _get_cell_key(ip)
    exec_count = ip.execution_count

    try:
        # Ensure the target directory exists
        _active_folder.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create directory {_active_folder}: {e}")
        return None # Indicate failure

    # Clean up images from previous execution of the same cell
    if _state.get(key) != exec_count:
        for old_file in _active_folder.glob(f"{key}_*.{fmt}"):
            try:
                old_file.unlink()
                logger.debug(f"Removed old image: {old_file.name}")
            except OSError as e:
                logger.warning(f"Failed to remove old image {old_file}: {e}")
        _state[key] = exec_count
        idx = 1
    else:
        # Increment index for multiple figures in the same cell execution
        idx = len(list(_active_folder.glob(f"{key}_*.{fmt}"))) + 1

    filename = f"{key}_{idx}.{fmt}"
    filepath = _active_folder / filename

    try:
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight", format=fmt)
        logger.info(f"Saved figure: {filepath.relative_to(Path.cwd())}")
    except Exception as e:
        logger.error(f"Failed to save figure {filepath}: {e}")
        return None # Indicate failure

    # Return HTML linking to the saved image with cache busting
    # Use relative path from notebook's perspective (assuming notebook is in CWD)
    # Note: This assumes the notebook server CWD matches the kernel CWD.
    #       In some setups (like remote kernels), this might need adjustment.
    rel_path = f"{_active_folder.name}/{filename}" # Relative to notebook dir
    return f'<img src="{rel_path}?v={exec_count}" alt="{filename}" style="max-width:100%;">'

def _no_op_repr_png(fig: Figure):
    """Prevents the default PNG representation."""
    return None

def _patch_figure_reprs(ip):
    """Applies the monkey-patches to the Figure class."""
    global _patch_applied
    if not ip:
        logger.warning("Cannot patch Figure: IPython kernel not found.")
        return

    # Disable default PNG embedding
    try:
        if hasattr(ip.display_formatter.formatters['image/png'], 'enabled'):
             ip.display_formatter.formatters['image/png'].enabled = False
    except KeyError:
        logger.warning("Could not disable 'image/png' formatter.")

    # Patch Figure methods
    Figure._repr_png_ = _no_op_repr_png
    # Use a lambda to capture the current ip and folder
    Figure._repr_html_ = lambda fig: _save_figure_and_get_html(fig, ip)
    _patch_applied = True
    logger.debug("Applied Figure repr patches.")

def _restore_figure_reprs(ip):
    """Restores original Figure representations (best effort)."""
    global _patch_applied
    if not _patch_applied:
        return
    # This requires storing the original methods, which we aren't doing yet.
    # For now, just remove our patches if possible.
    if hasattr(Figure, '_repr_png_') and Figure._repr_png_ is _no_op_repr_png:
        del Figure._repr_png_ # Or try to restore original if saved
    if hasattr(Figure, '_repr_html_') and callable(Figure._repr_html_):
         # Can't easily tell if it's our lambda, so potentially risky
         # del Figure._repr_html_ # Or restore original
         pass # For now, leave _repr_html_ potentially patched

    try:
        if hasattr(ip.display_formatter.formatters['image/png'], 'enabled'):
             ip.display_formatter.formatters['image/png'].enabled = True
    except KeyError:
        pass # Ignore if formatter doesn't exist

    _patch_applied = False
    logger.debug("Attempted to restore Figure repr patches.")


def _post_cell_cleanup_and_repatch(ip):
    """Closes figures and re-applies patches after cell execution."""
    if not ip:
        return

    # Close all figures to prevent memory leaks and duplicate output
    try:
        plt.close('all')
        logger.debug("Closed all matplotlib figures.")
    except Exception as e:
        logger.warning(f"Exception during plt.close('all'): {e}")

    # Re-apply patches in case the backend was changed or reset
    _patch_figure_reprs(ip)

def _clean_unused_images_logic() -> dict:
    """Deletes image files whose keys are not in the current state."""
    global _state, _active_folder
    deleted_files = []
    failed_deletions = []
    kept_files = []

    if not _active_folder.exists():
        logger.info(f"Image directory '{_active_folder}' does not exist. Nothing to clean.")
        return {"deleted": [], "failed": [], "kept": [], "message": "Image directory not found."}

    current_keys = set(_state.keys())
    logger.debug(f"Current cell keys in state: {current_keys}")

    for img_file in _active_folder.glob("*.png"):
        try:
            # Extract key (hash part) from filename like 'hash_idx.png'
            key_part = img_file.stem.split('_')[0]
            if key_part not in current_keys:
                try:
                    img_file.unlink()
                    deleted_files.append(str(img_file.relative_to(Path.cwd())))
                    logger.debug(f"Deleted unused image: {img_file.name}")
                except OSError as e:
                    failed_deletions.append(str(img_file.relative_to(Path.cwd())))
                    logger.warning(f"Failed to delete {img_file}: {e}")
            else:
                 kept_files.append(str(img_file.relative_to(Path.cwd())))
        except IndexError:
            logger.warning(f"Could not parse key from filename: {img_file.name}")
            kept_files.append(str(img_file.relative_to(Path.cwd()))) # Keep if format is unexpected
        except Exception as e:
             logger.error(f"Error processing file {img_file}: {e}")
             failed_deletions.append(str(img_file.relative_to(Path.cwd())))

    message = f"Cleaned {_active_folder}. Deleted: {len(deleted_files)}, Failed: {len(failed_deletions)}, Kept: {len(kept_files)}."
    logger.info(message)
    return {"deleted": deleted_files, "failed": failed_deletions, "kept": kept_files, "message": message} 