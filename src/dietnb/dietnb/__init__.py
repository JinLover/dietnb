from pathlib import Path
from IPython import get_ipython
from typing import Optional

# Import core logic and expose public functions
from . import _core

# Keep track of registered events to allow unloading
_post_run_cell_handler = None

def activate(ipython_instance=None):
    """Activates dietnb: Patches matplotlib Figure representation in IPython.

    Args:
        ipython_instance: Optional IPython shell instance. Auto-detected if None.
    """
    global _post_run_cell_handler

    ip = ipython_instance if ipython_instance else get_ipython()

    if not ip:
        # Consider if a print warning is desired here if logging is removed
        return

    # Apply the core patches, passing the ipython instance
    _core._patch_figure_reprs(ip)

    if _post_run_cell_handler:
        try:
            ip.events.unregister('post_run_cell', _post_run_cell_handler)
        except ValueError:
            pass 

    def handler(_):
        _core._post_cell_cleanup_and_repatch(ip) 

    _post_run_cell_handler = handler
    ip.events.register('post_run_cell', _post_run_cell_handler)

def deactivate(ipython_instance=None):
    """Deactivates dietnb: Restores original matplotlib Figure representation (best effort)."""
    global _post_run_cell_handler
    ip = ipython_instance if ipython_instance else get_ipython()

    if not ip:
        return

    _core._restore_figure_reprs(ip)

    if _post_run_cell_handler:
        try:
            ip.events.unregister('post_run_cell', _post_run_cell_handler)
            _post_run_cell_handler = None
        except ValueError:
            pass # Consider print warning

def clean_unused() -> dict:
    """Cleans up image files not associated with the current kernel state
    based on auto-detected notebook path or default folder.
    """
    return _core._clean_unused_images_logic()

__all__ = ['activate', 'deactivate', 'clean_unused'] 