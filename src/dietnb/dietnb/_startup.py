import dietnb
import logging

logger = logging.getLogger("dietnb_startup")

# Attempt to activate dietnb
try:
    dietnb.activate() # Call activate without folder_prefix for auto-detection
    logger.info("dietnb auto-activated via startup script.")
except Exception as e:
    logger.error(f"Error auto-activating dietnb via startup script: {e}", exc_info=True)