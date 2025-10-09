import hashlib
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Set, Tuple

# Removed imports for notebook and requests
# import matplotlib.pyplot as plt # This should be kept
# from IPython import get_ipython # This should be kept
# from matplotlib.figure import Figure # This should be kept

import matplotlib.pyplot as plt
from IPython import get_ipython
from matplotlib.figure import Figure

# Global state
_patch_applied = False
DEFAULT_FOLDER_NAME = "dietnb_imgs"


def _directory_key(directory: Path) -> str:
    """Returns a stable string representation for directory lookups."""
    try:
        return str(directory.resolve(strict=False))
    except OSError:
        return str(directory)


def _relative_to_cwd(path: Path) -> str:
    """Formats a path relative to the current working directory when possible."""
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _safe_relpath(path: Path, base: Path) -> Optional[str]:
    """Returns a POSIX-style relative path if possible."""
    try:
        rel = path.relative_to(base)
    except ValueError:
        try:
            rel = Path(os.path.relpath(path, base))
        except ValueError:
            return None
    return rel.as_posix()


def _img_src_relative_path(filepath: Path, notebook_path: Optional[Path]) -> str:
    """Computes an image src suitable for HTML, preferring notebook-relative paths."""
    if notebook_path:
        base = notebook_path.parent
        rel = _safe_relpath(filepath, base)
        if rel:
            return rel

    rel_cwd = _safe_relpath(filepath, Path.cwd())
    if rel_cwd:
        return rel_cwd

    return filepath.name


def _normalize_notebook_path(candidate: Optional[str]) -> Optional[Path]:
    """Normalizes notebook paths from various front-ends."""
    if not isinstance(candidate, str):
        return None

    candidate = candidate.strip()
    if not candidate:
        return None

    path = Path(candidate).expanduser()
    try:
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve(strict=False)
        else:
            path = path.resolve(strict=False)
    except (OSError, RuntimeError):
        return None

    return path if path.suffix.lower() == ".ipynb" else None


def _resolve_notebook_path(ip_instance) -> Optional[Path]:
    """Attempts to deduce the active notebook path from IPython metadata."""
    candidates = []

    if ip_instance:
        kernel = getattr(ip_instance, "kernel", None)
        session = getattr(kernel, "session", None)
        path_attr = getattr(session, "path", None)
        if isinstance(path_attr, str):
            candidates.append(path_attr)

        if hasattr(ip_instance, "user_global_ns"):
            vsc_path = ip_instance.user_global_ns.get("__vsc_ipynb_file__")
            if isinstance(vsc_path, str):
                candidates.append(vsc_path)

    env_path = os.environ.get("JPY_SESSION_NAME")
    if isinstance(env_path, str):
        candidates.append(env_path)

    for candidate in candidates:
        normalized = _normalize_notebook_path(candidate)
        if normalized:
            return normalized

    return None


@dataclass
class _FigureRegistry:
    """Tracks execution counts and per-cell figure indices."""

    _last_exec_per_cell: Dict[Tuple[str, str], int] = field(default_factory=dict)
    _indices: Dict[Tuple[str, str, int], int] = field(default_factory=dict)

    def register(self, directory: Path, cell_key: str, exec_count: int) -> Tuple[int, bool]:
        """Returns new index and whether this is a fresh execution for the cell."""
        dir_key = _directory_key(directory)
        state_key = (dir_key, cell_key)
        counter_key = (dir_key, cell_key, exec_count)

        last_exec = self._last_exec_per_cell.get(state_key)
        if last_exec != exec_count:
            self._last_exec_per_cell[state_key] = exec_count
            self._indices[counter_key] = 1
            self._drop_old_indices(dir_key, cell_key, exec_count)
            return 1, True

        next_idx = self._indices.get(counter_key, 1) + 1
        self._indices[counter_key] = next_idx
        return next_idx, False

    def active_cell_keys(self, directory: Path) -> Set[str]:
        """Returns all cell keys known for the provided directory."""
        dir_key = _directory_key(directory)
        return {
            cell_key
            for (stored_dir, cell_key), _ in self._last_exec_per_cell.items()
            if stored_dir == dir_key
        }

    def _drop_old_indices(self, dir_key: str, cell_key: str, exec_count: int) -> None:
        stale_keys = [
            key for key in self._indices
            if key[0] == dir_key and key[1] == cell_key and key[2] != exec_count
        ]
        for key in stale_keys:
            del self._indices[key]


_registry = _FigureRegistry()

def _get_notebook_image_dir(ip_instance, base_folder_name=DEFAULT_FOLDER_NAME) -> Path:
    """Determines the target image directory.
    Priority:
    1. Auto-detected notebook name.
    2. Default directory.
    """
    fallback_dir = Path.cwd() / base_folder_name
    notebook_path = _resolve_notebook_path(ip_instance)

    if notebook_path:
        notebook_dir_name_part = f"{notebook_path.stem}_{base_folder_name}" if notebook_path.stem else base_folder_name
        target_dir = notebook_path.parent / notebook_dir_name_part
    else:
        target_dir = fallback_dir

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir
    except OSError:
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir

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
    if not ip:
        return None

    # Determine target directory dynamically (no folder_prefix)
    image_dir = _get_notebook_image_dir(ip)

    key = _get_cell_key(ip)
    # Use execution_count if available, otherwise fallback (timestamp for uniqueness)
    exec_count = getattr(ip, "execution_count", None)
    if exec_count is None:
        exec_count = int(time.time() * 1000)

    idx, is_new_exec = _registry.register(image_dir, key, exec_count)
    if is_new_exec:
        _delete_previous_cell_images(image_dir, key)


    # Filename format: {exec_count}_{fig_index}_{cell_key}.png
    filename = f"{exec_count}_{idx}_{key}.png"
    filepath = image_dir / filename
    notebook_path = _resolve_notebook_path(ip)

    try:
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight", format=fmt)
    except Exception:
        return None # Indicate failure

    img_src = _img_src_relative_path(filepath, notebook_path)

    # Check if running in VS Code to add cache-busting query string specifically for it
    # ip is the IPython instance passed to _save_figure_and_get_html
    if ip and hasattr(ip, 'user_global_ns'):
        vsc_notebook_file_path_str = ip.user_global_ns.get("__vsc_ipynb_file__")
        if vsc_notebook_file_path_str and isinstance(vsc_notebook_file_path_str, str):
            # Placeholder: VS Code specific adjustments could be applied here if needed.
            img_src = f"{img_src}"

    # No /files/ prefix
    return f'<img src="{img_src}" alt="{filename}" style="max-width:100%;">'

def _no_op_repr_png(fig: Figure):
    """Prevents the default PNG representation."""
    return None


def _delete_previous_cell_images(image_dir: Path, cell_key: str) -> None:
    """Removes images generated by prior executions of the same cell."""
    pattern = f"*_*_{cell_key}.png"
    for old_file in image_dir.glob(pattern):
        try:
            old_file.unlink()
        except OSError:
            # Best effort cleanup; ignore permission issues.
            pass

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
    current_keys_in_state = _registry.active_cell_keys(image_dir)

    cleaned_count = 0
    failed_count = 0
    kept_count = 0

    for img_file in image_dir.glob("*.png"):
        try:
            # Extract key from filename like 'exec_count_idx_key.png'
            parts = img_file.stem.split('_')
            if len(parts) >= 3:
                key_part = parts[-1] # Key is the last part
                if key_part not in current_keys_in_state:
                    try:
                        img_file.unlink()
                        deleted_files.append(_relative_to_cwd(img_file))
                        cleaned_count += 1
                    except OSError:
                        failed_deletions.append(_relative_to_cwd(img_file))
                        failed_count += 1
                else:
                    kept_files.append(_relative_to_cwd(img_file))
                    kept_count += 1
            else:
                # Filename doesn't match expected format, keep it
                kept_files.append(_relative_to_cwd(img_file))
                kept_count += 1

        except Exception:
            # Catch any other parsing errors and keep the file
            failed_deletions.append(_relative_to_cwd(img_file))
            failed_count += 1

    message = f"Cleaned directory '{image_dir.name}'. Deleted: {cleaned_count}, Failed: {failed_count}, Kept: {kept_count}."
    return {"deleted": deleted_files, "failed": failed_deletions, "kept": kept_files, "message": message}
