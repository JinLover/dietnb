import dietnb
import logging

# Configure a basic logger for the startup script itself to aid debugging if needed.
logger = logging.getLogger("dietnb_startup")

# Attempt to activate dietnb
try:
    dietnb.activate() # Call activate without folder_prefix for auto-detection
    logger.info("dietnb auto-activated via startup script.")
    # You can print a message to the console if desired, but it might be verbose for a startup script.
    # print("[dietnb] Auto-activated. Matplotlib figures will be saved externally.")
except Exception as e:
    logger.error(f"Error auto-activating dietnb via startup script: {e}", exc_info=True)
    # Optionally, print a warning to the console so the user is aware of the failure.
    # print(f"[dietnb] Warning: Failed to auto-activate: {e}") 