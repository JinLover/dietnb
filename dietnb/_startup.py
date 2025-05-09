import dietnb
# import logging # Removed

# logger = logging.getLogger("dietnb_startup") # Removed

# Attempt to activate dietnb
try:
    dietnb.activate() # Call activate without folder_prefix for auto-detection
    # logger.info("dietnb auto-activated via startup script.") # Removed
    # You can print a message to the console if desired, but it might be verbose for a startup script.
    # print("[dietnb] Auto-activated. Matplotlib figures will be saved externally.")
except Exception as e:
    # logger.error(f"Error auto-activating dietnb via startup script: {e}", exc_info=True) # Removed
    # print(f"[dietnb] Warning: Failed to auto-activate: {e}") # Potentially keep this print for user feedback
    pass # Fail silently, or print a non-logging warning to console 