import logging
import sys

logger = logging.getLogger(__name__)

try:
    # Check if running in an IPython session
    # This check might be refined depending on exact context where startup scripts run
    from IPython import get_ipython
    ip = get_ipython()
    if ip:
        logger.debug("Importing dietnb in IPython startup script.")
        try:
            import dietnb
            dietnb.activate()
            logger.info("dietnb activated automatically via startup script.")
        except ImportError:
            logger.error("Failed to import dietnb. Ensure it is installed.")
        except Exception as e:
            logger.error(f"Error activating dietnb during startup: {e}")
    else:
        logger.debug("Not an IPython session, dietnb startup script skipped.")
except ImportError:
    # IPython itself is not available
    logger.debug("IPython not found, dietnb startup script skipped.")
except Exception as e:
    # Catch any other unexpected errors during startup check
    logger.error(f"Unexpected error in dietnb startup script: {e}", exc_info=True) 