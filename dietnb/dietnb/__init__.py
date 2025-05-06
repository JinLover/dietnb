import logging
from pathlib import Path
from IPython import get_ipython

# Import core logic and expose public functions
from . import _core

# Configure logging for the package
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Keep track of registered events to allow unloading
_post_run_cell_handler = None

def activate(folder="dietnb_imgs"):
    """Activates dietnb: Patches matplotlib Figure representation in IPython."""
    global _post_run_cell_handler
    ip = get_ipython()
    if not ip:
        logger.error("dietnb requires an active IPython kernel.")
        return

    # Update the active folder used by the core module
    _core._active_folder = Path.cwd() / folder
    logger.info(f"dietnb activated. Images will be saved to: {_core._active_folder}")

    # Apply the core patches
    _core._patch_figure_reprs(ip)

    # Register post-cell cleanup and repatching
    # Unregister previous handler first if activate is called again
    if _post_run_cell_handler:
        try:
            ip.events.unregister('post_run_cell', _post_run_cell_handler)
            logger.debug("Unregistered previous post_run_cell handler.")
        except ValueError:
            pass # Ignore if not registered

    # Define the handler using the current ip instance
    def handler(_):
        _core._post_cell_cleanup_and_repatch(ip)

    _post_run_cell_handler = handler # Store reference for potential unregistering
    ip.events.register('post_run_cell', _post_run_cell_handler)
    logger.debug("Registered post_run_cell handler.")

def deactivate():
    """Deactivates dietnb: Restores original matplotlib Figure representation (best effort)."""
    global _post_run_cell_handler
    ip = get_ipython()
    if not ip:
        logger.warning("IPython kernel not found. Cannot deactivate properly.")
        return

    # Attempt to restore original representations
    _core._restore_figure_reprs(ip)

    # Unregister the event handler
    if _post_run_cell_handler:
        try:
            ip.events.unregister('post_run_cell', _post_run_cell_handler)
            _post_run_cell_handler = None # Clear reference
            logger.info("dietnb deactivated. Unregistered event handler.")
        except ValueError:
            logger.warning("Could not unregister post_run_cell handler.")
    else:
        logger.info("dietnb deactivated (handler was not registered).")

def clean_unused() -> dict:
    """Cleans up image files not associated with the current kernel state."""
    # Ensure core module knows the folder (in case activate wasn't called recently)
    # This assumes activate sets the folder correctly first.
    if not _core._active_folder:
         logger.warning("Cannot clean images: target folder not set. Call activate() first.")
         return {"deleted": [], "failed": [], "kept": [], "message": "Target folder not set."}

    logger.info(f"Cleaning unused images in: {_core._active_folder}")
    return _core._clean_unused_images_logic()

# Make functions easily available
__all__ = ['activate', 'deactivate', 'clean_unused'] 