import logging
from pathlib import Path
from IPython import get_ipython

# Import core logic and expose public functions
from . import _core

# Configure logging for the package
# logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# We will set up more specific logging in activate()
logger = logging.getLogger(__name__) # This is 'dietnb'

# Keep track of registered events to allow unloading
_post_run_cell_handler = None

def activate(ipython_instance=None, folder="dietnb_imgs"):
    """Activates dietnb: Patches matplotlib Figure representation in IPython."""
    global _post_run_cell_handler

    # --- Enhanced Logging Setup ---
    # Get the root logger for 'dietnb' and its children like 'dietnb._core', 'dietnb._ipython'
    dietnb_root_logger = logging.getLogger('dietnb')
    dietnb_root_logger.setLevel(logging.DEBUG) # Set to DEBUG for development

    # Ensure at least one handler is present to see output, e.g., a StreamHandler for console.
    # This prevents issues if no root config was called or if handlers were cleared.
    if not dietnb_root_logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        dietnb_root_logger.addHandler(console_handler)
        # Also ensure propagation is not disabled if adding a handler here for the first time
        dietnb_root_logger.propagate = False 
    # --- End Enhanced Logging Setup ---

    # If ipython_instance is not provided, try to get it.
    ip = ipython_instance if ipython_instance else get_ipython()

    if not ip:
        # Use our own logger now that it's configured
        logging.getLogger('dietnb').error("dietnb requires an active IPython kernel.")
        return

    # Now use the configured logger
    current_logger = logging.getLogger('dietnb') 
    current_logger.info(f"dietnb activating. Figures will be saved based on notebook path or to '{_core.DEFAULT_FOLDER_NAME}'.")
    current_logger.debug(f"IPython instance: {ip}")
    current_logger.debug(f"Target base folder name: {folder}") # folder arg is not used yet by _core

    # Apply the core patches, passing the ipython instance
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

def deactivate(ipython_instance=None):
    """Deactivates dietnb: Restores original matplotlib Figure representation (best effort)."""
    global _post_run_cell_handler
    current_logger = logging.getLogger('dietnb') # Use configured logger

    ip = ipython_instance if ipython_instance else get_ipython()

    if not ip:
        current_logger.warning("IPython kernel not found. Cannot deactivate properly.")
        return

    # Attempt to restore original representations
    _core._restore_figure_reprs(ip)

    # Unregister the event handler
    if _post_run_cell_handler:
        try:
            ip.events.unregister('post_run_cell', _post_run_cell_handler)
            _post_run_cell_handler = None # Clear reference
            current_logger.info("dietnb deactivated. Unregistered event handler.")
        except ValueError:
            current_logger.warning("Could not unregister post_run_cell handler.")
    else:
        current_logger.info("dietnb deactivated (handler was not registered).")

def clean_unused() -> dict:
    """Cleans up image files not associated with the current kernel state for the current notebook."""
    logger.info(f"Cleaning unused images in the directory associated with the current notebook context...")
    return _core._clean_unused_images_logic()

# Make functions easily available
__all__ = ['activate', 'deactivate', 'clean_unused'] 