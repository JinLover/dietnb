import hashlib
import logging
import warnings
from pathlib import Path
from typing import Optional, Tuple
import time
import os

import matplotlib.pyplot as plt
from IPython import get_ipython
from matplotlib.figure import Figure

# Global state
_state = {}  # Stores {cell_key: last_exec_count}
_patch_applied = False
_current_folder_prefix: Optional[str] = None # Store prefix at module level for repatching

# Configure logging
logger = logging.getLogger(__name__)

DEFAULT_FOLDER_NAME = "dietnb_imgs"

def _get_notebook_image_dir(ip_instance, folder_prefix: Optional[str] = None, base_folder_name=DEFAULT_FOLDER_NAME) -> Path:
    """Determines the target image directory.
    Priority:
    1. User-provided folder_prefix.
    2. Auto-detected notebook name.
    3. Default directory.
    """
    logger = logging.getLogger('dietnb._core')
    default_dir_for_fallback = Path(os.getcwd()) / base_folder_name
    notebook_path_str: Optional[str] = None
    detection_method: Optional[str] = None

    # --- PRIORITY 0: User-provided folder_prefix ---
    if folder_prefix:
        if not isinstance(folder_prefix, str) or not folder_prefix.strip():
            logger.warning(f"Invalid folder_prefix '{folder_prefix}' provided. Will attempt auto-detection or fallback.")
        else:
            target_dir_name = f"{folder_prefix.strip()}_{base_folder_name}"
            # Place the dir in CWD if prefix is given, for simplicity and predictability
            target_dir = Path(os.getcwd()) / target_dir_name
            logger.info(f"Using user-provided folder_prefix to create directory: {target_dir}")
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                return target_dir
            except OSError as e:
                logger.error(f"Failed to create directory {target_dir} with prefix: {e}. Falling back.")
                # Fall through to auto-detection or default if creation fails

    # --- PRIORITY 1: Standard ip.kernel.session.path (if no valid prefix was used) ---
    if ip_instance and hasattr(ip_instance, 'kernel') and ip_instance.kernel and \
       hasattr(ip_instance.kernel, 'session') and ip_instance.kernel.session:
        notebook_path_attr = getattr(ip_instance.kernel.session, 'path', None)
        if isinstance(notebook_path_attr, str) and notebook_path_attr.strip():
            notebook_path_str = notebook_path_attr.strip()
            detection_method = "ip.kernel.session.path"
            logger.debug(f"Detected path via {detection_method}: {notebook_path_str}")
        else:
             logger.debug(f"ip.kernel.session.path attribute was not a valid string: '{notebook_path_attr}'")

    # --- PRIORITY 2: VS Code __vsc_ipynb_file__ (from user_global_ns) ---
    if not notebook_path_str and ip_instance and hasattr(ip_instance, 'user_global_ns'):
        vsc_path = ip_instance.user_global_ns.get("__vsc_ipynb_file__")
        if isinstance(vsc_path, str) and vsc_path.strip():
            notebook_path_str = vsc_path.strip()
            detection_method = "__vsc_ipynb_file__ (from user_global_ns)"
            logger.debug(f"Detected path via {detection_method}: {notebook_path_str}")
        else:
             logger.debug(f"__vsc_ipynb_file__ not found or invalid in ip.user_global_ns: '{vsc_path}'")
    elif not notebook_path_str:
        logger.debug("Could not attempt __vsc_ipynb_file__ check: ip_instance or user_global_ns not available.")

    # --- PRIORITY 3: Jupyter JPY_SESSION_NAME ---
    if not notebook_path_str:
        jpy_session_name = os.environ.get("JPY_SESSION_NAME")
        if isinstance(jpy_session_name, str) and jpy_session_name.strip():
            # Assume it might be relative to CWD if not absolute
            potential_path = jpy_session_name.strip()
            if not os.path.isabs(potential_path):
                 potential_path = os.path.join(os.getcwd(), potential_path)
                 logger.debug(f"JPY_SESSION_NAME was relative, resolved to: {potential_path}")

            # Basic check if the resolved path looks like a notebook file
            if os.path.isfile(potential_path) and potential_path.lower().endswith('.ipynb'):
                 notebook_path_str = potential_path
                 detection_method = "JPY_SESSION_NAME"
                 logger.debug(f"Detected path via {detection_method}: {notebook_path_str}")
            else:
                 logger.debug(f"JPY_SESSION_NAME ('{jpy_session_name}') resolved to '{potential_path}', which is not a valid notebook file.")
        else:
            logger.debug(f"JPY_SESSION_NAME environment variable not found or not a valid string: '{jpy_session_name}'")


    # --- Process the detected path or fallback ---
    if notebook_path_str and detection_method:
        try:
            notebook_path = Path(notebook_path_str)
            notebook_fname = notebook_path.name
            notebook_name_without_ext, _ = os.path.splitext(notebook_fname)

            if not notebook_name_without_ext:
                 logger.warning(f"Could not extract valid name from path '{notebook_path_str}' (method: {detection_method}). Falling back.")
                 target_dir = default_dir_for_fallback
            else:
                 notebook_dir_name_part = f"{notebook_name_without_ext}_{base_folder_name}"
                 # Place the dir next to the notebook file
                 target_dir_base = notebook_path.parent
                 target_dir = target_dir_base / notebook_dir_name_part
                 logger.info(f"Using notebook-specific image directory via {detection_method}: {target_dir}")

        except Exception as e:
            logger.error(f"Error processing path '{notebook_path_str}' (method: {detection_method}): {e}. Falling back.")
            target_dir = default_dir_for_fallback
    else:
        logger.info(f"Failed to detect notebook path via all methods and no valid folder_prefix. Falling back to default directory: {default_dir_for_fallback}")
        target_dir = default_dir_for_fallback

    # Ensure directory exists and return Path object
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir
    except OSError as e:
        logger.error(f"Failed to create target directory {target_dir}: {e}. Returning default {default_dir_for_fallback} as last resort.")
        default_dir_for_fallback.mkdir(parents=True, exist_ok=True) # Try creating default dir if target failed
        return default_dir_for_fallback

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

def _save_figure_and_get_html(fig: Figure, ip, folder_prefix: Optional[str] = None, fmt="png", dpi=150) -> Optional[str]:
    """Saves the figure to a file and returns an HTML img tag."""
    global _state
    logger_core = logging.getLogger('dietnb._core') # Explicitly get core logger
    if not ip:
        logger_core.error("IPython kernel not found. Cannot save figure.")
        return None

    # Determine target directory dynamically, passing folder_prefix
    image_dir = _get_notebook_image_dir(ip, folder_prefix=folder_prefix)

    key = _get_cell_key(ip)
    # Use execution_count if available, otherwise fallback (e.g., timestamp for uniqueness)
    exec_count = getattr(ip, 'execution_count', None) or int(time.time())


    try:
        # Ensure the target directory exists
        image_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger_core.error(f"Failed to create directory {image_dir}: {e}")
        return None # Indicate failure

    # Use a tuple (directory, cell_key) for state to handle multiple notebooks
    state_key = (str(image_dir), key)

    # Clean up images from previous execution of the same cell *in the same directory*
    if _state.get(state_key) != exec_count:
        for old_file in image_dir.glob(f"{key}_*.{fmt}"):
            try:
                old_file.unlink()
                logger_core.debug(f"Removed old image: {old_file.name} in {image_dir.name}")
            except OSError as e:
                logger_core.warning(f"Failed to remove old image {old_file}: {e}")
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
        logger_core.info(f"Saved figure: {log_path}")
    except Exception as e:
        logger_core.error(f"Failed to save figure {filepath}: {e}")
        return None # Indicate failure

    # Return HTML linking to the saved image with cache busting
    # Use relative path *from notebook's perspective* (assuming kernel CWD = notebook dir)
    rel_path = f"{image_dir.name}/{filename}" # Use the determined directory name
    return f'<img src="{rel_path}?v={exec_count}" alt="{filename}" style="max-width:100%;">'

def _no_op_repr_png(fig: Figure):
    """Prevents the default PNG representation."""
    return None

def _patch_figure_reprs(ip, folder_prefix: Optional[str] = None):
    """Applies the monkey-patches to the Figure class."""
    global _patch_applied, _current_folder_prefix
    logger_core = logging.getLogger('dietnb._core') # Explicitly get core logger
    if not ip:
        logger_core.warning("Cannot patch Figure: IPython kernel not found.")
        return

    _current_folder_prefix = folder_prefix # Store for re-patching

    # Disable default PNG embedding
    try:
        if hasattr(ip.display_formatter.formatters['image/png'], 'enabled'):
             ip.display_formatter.formatters['image/png'].enabled = False
    except KeyError:
        logger_core.warning("Could not disable 'image/png' formatter.")

    # Patch Figure methods
    Figure._repr_png_ = _no_op_repr_png
    # Use a lambda to capture the current ip and folder_prefix
    Figure._repr_html_ = lambda fig_obj: _save_figure_and_get_html(fig_obj, ip, folder_prefix=_current_folder_prefix)
    _patch_applied = True
    logger_core.debug(f"Applied Figure repr patches. Folder prefix: '{_current_folder_prefix}'.")

def _restore_figure_reprs(ip):
    """Restores original Figure representations (best effort)."""
    global _patch_applied, _current_folder_prefix
    logger_core = logging.getLogger('dietnb._core') # Explicitly get core logger
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
    _current_folder_prefix = None # Reset prefix
    logger_core.debug("Attempted to restore Figure repr patches.")


def _post_cell_cleanup_and_repatch(ip, folder_prefix: Optional[str] = None):
    """Closes figures and re-applies patches after cell execution."""
    logger_core = logging.getLogger('dietnb._core') # Explicitly get core logger
    if not ip:
        return

    # Close all figures to prevent memory leaks and duplicate output
    # plt.close should be safe regardless of saving directory
    try:
        # Only close figures managed by plt.figure(), not necessarily all Figure objects
        # Check if there are any active pyplot figures
        if plt.get_fignums():
             plt.close('all')
             logger_core.debug("Closed all active pyplot figures.")
        else:
             logger_core.debug("No active pyplot figures to close.")
    except Exception as e:
        logger_core.warning(f"Exception during plt.close('all'): {e}")

    # Re-apply patches in case the backend was changed or reset
    # Pass the folder_prefix that was active during this cell's context
    _patch_figure_reprs(ip, folder_prefix)

def _clean_unused_images_logic(folder_prefix: Optional[str] = None) -> dict:
    """Deletes image files whose keys are not in the current state *for the current context*."""
    global _state
    logger_core = logging.getLogger('dietnb._core') # Explicitly get core logger
    deleted_files = []
    failed_deletions = []
    kept_files = []

    ip = get_ipython()
    if not ip:
        logger_core.warning("Cannot determine notebook context outside IPython. Skipping cleanup.")
        return {"deleted": [], "failed": [], "kept": [], "message": "Cleanup skipped: Not in IPython."}

    # Determine the directory for the *current* context, using folder_prefix if provided
    image_dir = _get_notebook_image_dir(ip, folder_prefix=folder_prefix)

    if not image_dir.exists():
        logger_core.info(f"Image directory '{image_dir}' does not exist. Nothing to clean.")
        return {"deleted": [], "failed": [], "kept": [], "message": f"Image directory '{image_dir.name}' not found."}

    # Get keys relevant *only* to the current directory from the state
    current_dir_str = str(image_dir)
    current_keys_in_state = {cell_key for (dir_key, cell_key) in _state if dir_key == current_dir_str}
    logger_core.debug(f"Keys currently active for directory '{image_dir.name}': {current_keys_in_state}")

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
                    logger_core.debug(f"Deleted unused image: {log_path}")
                    cleaned_count += 1
                except OSError as e:
                    log_path = img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file
                    failed_deletions.append(str(log_path))
                    logger_core.warning(f"Failed to delete {log_path}: {e}")
                    failed_count += 1
            else:
                log_path = img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file
                kept_files.append(str(log_path))
                kept_count += 1
        except IndexError:
            log_path = img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file
            logger_core.warning(f"Could not parse key from filename: {log_path}. Keeping file.")
            kept_files.append(str(log_path))
            kept_count += 1 # Treat as kept if format is unexpected
        except Exception as e:
            log_path = img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file
            logger_core.error(f"Error processing file {log_path}: {e}")
            failed_deletions.append(str(log_path))
            failed_count += 1

    message = f"Cleaned directory '{image_dir.name}'. Deleted: {cleaned_count}, Failed: {failed_count}, Kept: {kept_count}."
    logger.info(message)
    return {"deleted": deleted_files, "failed": failed_deletions, "kept": kept_files, "message": message} 