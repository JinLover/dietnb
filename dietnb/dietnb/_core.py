import hashlib
from pathlib import Path
from typing import Optional, Tuple
import time
import os
from urllib.parse import quote, urljoin
import json

# Attempt to import notebook and requests for get_jupyter_root_dir
try:
    from notebook import notebookapp
    import requests
except ImportError:
    notebookapp = None
    requests = None

import matplotlib.pyplot as plt
from IPython import get_ipython
from matplotlib.figure import Figure

# Global state
_state = {}  # Stores {cell_key: last_exec_count}
_patch_applied = False

DEFAULT_FOLDER_NAME = "dietnb_imgs"

# Function to get Jupyter server's root directory
# Moved before _get_notebook_image_dir for logical grouping if preferred, or ensure it's at module level
def get_jupyter_root_dir():
    """Returns the root directory path of the Jupyter server connected to the current kernel."""
    # Ensure get_ipython() can be called here, or it needs to be passed if used in a context where it's not global
    current_ipython_instance = get_ipython() # Explicitly get it for this function context
    if not notebookapp or not requests or not current_ipython_instance: # Check for dependencies and IPython
        return None

    try:
        kernel_config = current_ipython_instance.config
        if not kernel_config or "IPKernelApp" not in kernel_config or "connection_file" not in kernel_config["IPKernelApp"]:
            return None
        connection_file_path = kernel_config["IPKernelApp"]["connection_file"]
        # Use os.path.splitext for robustness in getting the stem for various kernel file name patterns
        connection_file_name_stem = Path(connection_file_path).stem.replace("kernel-", "")
    except Exception:
        return None # Error getting connection file info

    try:
        for srv in notebookapp.list_running_servers():
            try:
                # Correctly join URL parts using urllib.parse.urljoin
                sessions_url = urljoin(srv['url'], 'api/sessions')
                token = srv.get("token", "")
                if token:
                    sessions_url += f"?token={token}"
                
                r = requests.get(sessions_url, timeout=3) 
                r.raise_for_status() 
                sessions = r.json()

                for sess in sessions:
                    if 'kernel' in sess and 'id' in sess['kernel'] and \
                       sess['kernel']['id'] == connection_file_name_stem: # Exact match preferred if stem is just the ID
                        return srv.get('notebook_dir') 
            except (requests.RequestException, ValueError, KeyError, AttributeError, json.JSONDecodeError):
                continue 
    except Exception:
        return None
    
    return None

def _get_notebook_image_dir(ip_instance, base_folder_name=DEFAULT_FOLDER_NAME) -> Path:
    """Determines the target image directory.
    Priority:
    1. Auto-detected notebook name.
    2. Default directory.
    """
    default_dir_for_fallback = Path(os.getcwd()) / base_folder_name
    notebook_path_str: Optional[str] = None

    if ip_instance and hasattr(ip_instance, 'kernel') and ip_instance.kernel and \
       hasattr(ip_instance.kernel, 'session') and ip_instance.kernel.session:
        notebook_path_attr = getattr(ip_instance.kernel.session, 'path', None)
        if isinstance(notebook_path_attr, str) and notebook_path_attr.strip():
            notebook_path_str = notebook_path_attr.strip()

    if not notebook_path_str and ip_instance and hasattr(ip_instance, 'user_global_ns'):
        vsc_path = ip_instance.user_global_ns.get("__vsc_ipynb_file__")
        if isinstance(vsc_path, str) and vsc_path.strip():
            notebook_path_str = vsc_path.strip()

    if not notebook_path_str:
        jpy_session_name = os.environ.get("JPY_SESSION_NAME")
        if isinstance(jpy_session_name, str) and jpy_session_name.strip():
            potential_path = jpy_session_name.strip()
            if not os.path.isabs(potential_path):
                 potential_path = os.path.join(os.getcwd(), potential_path)
            if os.path.isfile(potential_path) and potential_path.lower().endswith('.ipynb'):
                 notebook_path_str = potential_path

    if notebook_path_str:
        try:
            notebook_path = Path(notebook_path_str)
            notebook_fname = notebook_path.name
            notebook_name_without_ext, _ = os.path.splitext(notebook_fname)

            if not notebook_name_without_ext:
                 target_dir = default_dir_for_fallback
            else:
                 notebook_dir_name_part = f"{notebook_name_without_ext}_{base_folder_name}"
                 target_dir_base = notebook_path.parent
                 target_dir = target_dir_base / notebook_dir_name_part
        except Exception:
            target_dir = default_dir_for_fallback
    else:
        target_dir = default_dir_for_fallback

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir
    except OSError:
        default_dir_for_fallback.mkdir(parents=True, exist_ok=True)
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
        return fallback_key

def _save_figure_and_get_html(fig: Figure, ip, fmt="png", dpi=150) -> Optional[str]:
    """Saves the figure to a file and returns an HTML img tag."""
    global _state
    if not ip:
        return None

    # Determine target directory dynamically (no folder_prefix)
    image_dir = _get_notebook_image_dir(ip)

    key = _get_cell_key(ip)
    # Use execution_count if available, otherwise fallback (e.g., timestamp for uniqueness)
    exec_count = getattr(ip, 'execution_count', None) or int(time.time())


    try:
        # Ensure the target directory exists
        image_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None # Indicate failure

    # Use a tuple (directory, cell_key) for state to handle multiple notebooks
    state_key = (str(image_dir), key)

    # Clean up images from previous execution of the same cell *in the same directory*
    if _state.get(state_key) != exec_count:
        for old_file in image_dir.glob(f"{key}_*.{fmt}"):
            try:
                old_file.unlink()
            except OSError:
                pass # Fail silently if old file removal fails
        _state[state_key] = exec_count
        idx = 1
    else:
        # Increment index for multiple figures in the same cell execution
        idx = len(list(image_dir.glob(f"{key}_*.{fmt}"))) + 1

    filename = f"{key}_{idx}.{fmt}"
    filepath = image_dir / filename

    try:
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight", format=fmt)
    except Exception:
        return None # Indicate failure

    # --- NEW SRC PATH LOGIC (ENVIRONMENT-AWARE + JUPYTER ROOT DETECTION) ---
    img_src_path_segment: str
    
    vsc_notebook_file_path_str = ip.user_global_ns.get("__vsc_ipynb_file__")

    if vsc_notebook_file_path_str and isinstance(vsc_notebook_file_path_str, str):
        # VS Code Environment: Use filesystem relative path
        try:
            current_notebook_abs_path = Path(vsc_notebook_file_path_str).resolve()
            current_notebook_dir_abs = current_notebook_abs_path.parent
            rel_path_os = os.path.relpath(filepath.resolve(), start=current_notebook_dir_abs)
            img_src_path_segment = str(Path(rel_path_os)).replace(os.sep, '/')
        except Exception: # Broad catch for any error in VSCode path logic
            img_src_path_segment = f"{image_dir.name}/{filename}"
    else:
        # Web Jupyter Environment (or other non-VSCode IPython console)
        server_root_dir_str = get_jupyter_root_dir()
        
        if server_root_dir_str:
            try:
                server_root_path = Path(server_root_dir_str).resolve()
                image_abs_path = filepath.resolve()
                path_relative_to_server_root = image_abs_path.relative_to(server_root_path)
                encoded_path_segment = quote(str(path_relative_to_server_root))
                img_src_path_segment = f"/files/{encoded_path_segment}"
            except Exception: 
                try:
                    path_relative_to_cwd = filepath.resolve().relative_to(Path(os.getcwd()).resolve())
                    img_src_path_segment = f"/files/{quote(str(path_relative_to_cwd))}"
                except Exception:
                    img_src_path_segment = f"/files/{quote(image_dir.name)}/{quote(filename)}"
        else:
            try:
                path_relative_to_cwd = filepath.resolve().relative_to(Path(os.getcwd()).resolve())
                img_src_path_segment = f"/files/{quote(str(path_relative_to_cwd))}"
            except Exception:
                img_src_path_segment = f"/files/{quote(image_dir.name)}/{quote(filename)}"

    img_src = f"{img_src_path_segment}?v={exec_count}"
    return f'<img src="{img_src}" alt="{filename}" style="max-width:100%;">'

def _no_op_repr_png(fig: Figure):
    """Prevents the default PNG representation."""
    return None

def _patch_figure_reprs(ip):
    """Applies the monkey-patches to the Figure class."""
    global _patch_applied
    if not ip:
        return

    # Disable default PNG embedding
    try:
        if hasattr(ip.display_formatter.formatters['image/png'], 'enabled'):
             ip.display_formatter.formatters['image/png'].enabled = False
    except KeyError:
        pass

    # Patch Figure methods
    Figure._repr_png_ = _no_op_repr_png
    # Use a lambda to capture the current ip
    Figure._repr_html_ = lambda fig_obj: _save_figure_and_get_html(fig_obj, ip)
    _patch_applied = True

def _restore_figure_reprs(ip):
    """Restores original Figure representations (best effort)."""
    global _patch_applied
    if not _patch_applied:
        return
    # This requires storing the original methods, which we aren't doing yet.
    # For now, just remove our patches if possible.
    if hasattr(Figure, '_repr_png_') and Figure._repr_png_ is _no_op_repr_png:
        del Figure._repr_png_ # Or try to restore original if saved
    # Cannot easily restore _repr_html_ due to lambda, so leave it for now
    try:
        if hasattr(ip.display_formatter.formatters['image/png'], 'enabled'):
             ip.display_formatter.formatters['image/png'].enabled = True
    except KeyError:
        pass # Ignore if formatter doesn't exist

    _patch_applied = False


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
    except Exception:
        pass

    # Re-apply patches in case the backend was changed or reset
    _patch_figure_reprs(ip)

def _clean_unused_images_logic() -> dict:
    """Deletes image files whose keys are not in the current state *for the current context*."""
    global _state
    deleted_files = []
    failed_deletions = []
    kept_files = []

    ip = get_ipython()
    if not ip:
        return {"deleted": [], "failed": [], "kept": [], "message": "Cleanup skipped: Not in IPython."}

    # Determine the directory for the *current* context (no folder_prefix)
    image_dir = _get_notebook_image_dir(ip)

    if not image_dir.exists():
        return {"deleted": [], "failed": [], "kept": [], "message": f"Image directory '{image_dir.name}' not found."}

    # Get keys relevant *only* to the current directory from the state
    current_dir_str = str(image_dir)
    current_keys_in_state = {cell_key for (dir_key, cell_key) in _state if dir_key == current_dir_str}

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
                    deleted_files.append(str(img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file))
                    cleaned_count += 1
                except OSError:
                    failed_deletions.append(str(img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file))
                    failed_count += 1
            else:
                kept_files.append(str(img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file))
                kept_count += 1
        except IndexError:
            kept_files.append(str(img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file))
            kept_count += 1 # Treat as kept if format is unexpected
        except Exception:
            failed_deletions.append(str(img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file))
            failed_count += 1

    message = f"Cleaned directory '{image_dir.name}'. Deleted: {cleaned_count}, Failed: {failed_count}, Kept: {kept_count}."
    return {"deleted": deleted_files, "failed": failed_deletions, "kept": kept_files, "message": message} 