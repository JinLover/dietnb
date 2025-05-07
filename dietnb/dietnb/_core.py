import hashlib
import logging
import warnings
from pathlib import Path
from typing import Optional, Tuple
import time

import matplotlib.pyplot as plt
from IPython import get_ipython
from matplotlib.figure import Figure

# Global state
_state = {}  # Stores {cell_key: last_exec_count}
# Removed _active_folder, will determine dynamically
_patch_applied = False

# Configure logging
logger = logging.getLogger(__name__)

DEFAULT_FOLDER_NAME = "dietnb_imgs"

def _get_notebook_image_dir(ip) -> Path:
    """Determines the target image directory based on the notebook name."""
    notebook_path_str = None
    try:
        # Attempt to get the notebook path relative to the server root
        if ip and hasattr(ip, 'kernel') and hasattr(ip.kernel, 'session') and hasattr(ip.kernel.session, 'path'):
            notebook_path_str = ip.kernel.session.path
            logger.debug(f"Detected notebook path: {notebook_path_str}")
        else:
            logger.debug("Could not detect notebook path from kernel session.")

    except Exception as e:
        logger.warning(f"Error detecting notebook path: {e}", exc_info=True)

    if notebook_path_str:
        try:
            # Construct path relative to CWD, assuming server root = CWD
            # This might need adjustment in complex setups (e.g., remote kernels, different server root)
            notebook_file_path = Path(notebook_path_str).resolve()
            # Check if path seems plausible (e.g., exists, though it might not if just renamed/moved)
            # notebook_dir = notebook_file_path.parent
            notebook_stem = notebook_file_path.stem
            folder_name = f"{notebook_stem}_dietnb_imgs"
            # Assume images are saved relative to the *current working directory*
            # which is usually where the notebook kernel is started.
            target_dir = Path.cwd() / folder_name
            logger.debug(f"Using notebook-specific image directory: {target_dir}")
            return target_dir
        except Exception as e:
            logger.warning(f"Error processing notebook path '{notebook_path_str}': {e}. Falling back to default.", exc_info=True)
            # Fallback to default if path processing fails
            pass

    # Fallback to default directory name if path not found or processing failed
    target_dir = Path.cwd() / DEFAULT_FOLDER_NAME
    logger.debug(f"Falling back to default image directory: {target_dir}")
    return target_dir

def _get_cell_key(ip) -> str:
    """Generates a unique key for the current cell execution."""
    if not ip:
        # Fallback if IPython is not available (e.g., plain Python script)
        # Use a simple counter or random hash, less ideal but functional
        # For now, stick to figure number if possible, but this is unreliable outside IPython
        fig = plt.gcf()
        return hashlib.sha1(str(id(fig)).encode()).hexdigest()[:12] # Less stable fallback

    # Prefer cellId from metadata (JupyterLab >= 3, VS Code, etc.)
    meta = ip.parent_header.get("metadata", {})
    cell_id = meta.get("cellId") or meta.get("cell_id")

    if cell_id:
        return hashlib.sha1(cell_id.encode()).hexdigest()[:12]

    # Fallback to hashing the raw cell content (less reliable)
    try:
        # Ensure history manager and raw history are available
        if hasattr(ip, 'history_manager') and hasattr(ip.history_manager, 'input_hist_raw') and ip.history_manager.input_hist_raw:
             raw_cell = ip.history_manager.input_hist_raw[-1]
             return hashlib.sha1(raw_cell.encode()).hexdigest()[:12]
        else:
             raise AttributeError("History manager or raw input history not available.")
    except (AttributeError, IndexError):
        # Fallback if history is not available or empty
        fig = plt.gcf()
        fallback_key = hashlib.sha1(str(id(fig)).encode()).hexdigest()[:12]
        warnings.warn(
            f"Could not reliably determine cell identity. Using less stable fallback key '{fallback_key}'. "
            f"Saving figures might overwrite previous ones unexpectedly if cell ID is unavailable.",
            stacklevel=2
        )
        return fallback_key

def _save_figure_and_get_html(fig: Figure, ip, fmt="png", dpi=150) -> Optional[str]:
    """Saves the figure to a file and returns an HTML img tag."""
    global _state # Only _state is global now
    if not ip:
        logger.error("IPython kernel not found. Cannot save figure.")
        return None

    # Determine target directory dynamically
    image_dir = _get_notebook_image_dir(ip)

    key = _get_cell_key(ip)
    # Use execution_count if available, otherwise fallback (e.g., timestamp for uniqueness)
    exec_count = getattr(ip, 'execution_count', None) or int(time.time())


    try:
        # Ensure the target directory exists
        image_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create directory {image_dir}: {e}")
        return None # Indicate failure

    # Use a tuple (directory, cell_key) for state to handle multiple notebooks
    state_key = (str(image_dir), key)

    # Clean up images from previous execution of the same cell *in the same directory*
    if _state.get(state_key) != exec_count:
        for old_file in image_dir.glob(f"{key}_*.{fmt}"):
            try:
                old_file.unlink()
                logger.debug(f"Removed old image: {old_file.name} in {image_dir.name}")
            except OSError as e:
                logger.warning(f"Failed to remove old image {old_file}: {e}")
        _state[state_key] = exec_count
        idx = 1
    else:
        # Increment index for multiple figures in the same cell execution
        idx = len(list(image_dir.glob(f"{key}_*.{fmt}"))) + 1

    filename = f"{key}_{idx}.{fmt}"
    filepath = image_dir / filename

    try:
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight", format=fmt)
        # Use relative path to CWD for logging clarity
        log_path = filepath.relative_to(Path.cwd()) if filepath.is_relative_to(Path.cwd()) else filepath
        logger.info(f"Saved figure: {log_path}")
    except Exception as e:
        logger.error(f"Failed to save figure {filepath}: {e}")
        return None # Indicate failure

    # Return HTML linking to the saved image with cache busting
    # Use relative path *from notebook's perspective* (assuming kernel CWD = notebook dir)
    rel_path = f"{image_dir.name}/{filename}" # Use the determined directory name
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
    # plt.close should be safe regardless of saving directory
    try:
        # Only close figures managed by plt.figure(), not necessarily all Figure objects
        # Check if there are any active pyplot figures
        if plt.get_fignums():
             plt.close('all')
             logger.debug("Closed all active pyplot figures.")
        else:
             logger.debug("No active pyplot figures to close.")
    except Exception as e:
        logger.warning(f"Exception during plt.close('all'): {e}")

    # Re-apply patches in case the backend was changed or reset
    # This doesn't depend on the save directory
    _patch_figure_reprs(ip)

def _clean_unused_images_logic() -> dict:
    """Deletes image files whose keys are not in the current state *for the current notebook*."""
    global _state
    deleted_files = []
    failed_deletions = []
    kept_files = []

    ip = get_ipython()
    if not ip:
        logger.warning("Cannot determine notebook context outside IPython. Skipping cleanup.")
        return {"deleted": [], "failed": [], "kept": [], "message": "Cleanup skipped: Not in IPython."}

    # Determine the directory for the *current* notebook (or default)
    image_dir = _get_notebook_image_dir(ip)

    if not image_dir.exists():
        logger.info(f"Image directory '{image_dir}' does not exist. Nothing to clean.")
        return {"deleted": [], "failed": [], "kept": [], "message": f"Image directory '{image_dir.name}' not found."}

    # Get keys relevant *only* to the current directory from the state
    current_dir_str = str(image_dir)
    current_keys_in_state = {cell_key for (dir_key, cell_key) in _state if dir_key == current_dir_str}
    logger.debug(f"Keys currently active for directory '{image_dir.name}': {current_keys_in_state}")

    cleaned_count = 0
    failed_count = 0
    kept_count = 0

    for img_file in image_dir.glob("*.png"):
        try:
            # Extract key (hash part) from filename like 'hash_idx.png'
            key_part = img_file.stem.split('_')[0]
            if key_part not in current_keys_in_state:
                try:
                    img_file.unlink()
                    log_path = img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file
                    deleted_files.append(str(log_path))
                    logger.debug(f"Deleted unused image: {log_path}")
                    cleaned_count += 1
                except OSError as e:
                    log_path = img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file
                    failed_deletions.append(str(log_path))
                    logger.warning(f"Failed to delete {log_path}: {e}")
                    failed_count += 1
            else:
                log_path = img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file
                kept_files.append(str(log_path))
                kept_count += 1
        except IndexError:
            log_path = img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file
            logger.warning(f"Could not parse key from filename: {log_path}. Keeping file.")
            kept_files.append(str(log_path))
            kept_count += 1 # Treat as kept if format is unexpected
        except Exception as e:
            log_path = img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file
            logger.error(f"Error processing file {log_path}: {e}")
            failed_deletions.append(str(log_path))
            failed_count += 1

    message = f"Cleaned directory '{image_dir.name}'. Deleted: {cleaned_count}, Failed: {failed_count}, Kept: {kept_count}."
    logger.info(message)
    return {"deleted": deleted_files, "failed": failed_deletions, "kept": kept_files, "message": message} 