import logging

from . import activate, deactivate

logger = logging.getLogger(__name__)

def load_ipython_extension(ipython):
    """Registers the activate function when the extension is loaded."""
    logger.debug("Loading dietnb IPython extension.")
    activate()
    print("dietnb extension loaded. Matplotlib figures will be saved externally.")

def unload_ipython_extension(ipython):
    """Registers the deactivate function when the extension is unloaded."""
    logger.debug("Unloading dietnb IPython extension.")
    deactivate()
    print("dietnb extension unloaded.") 