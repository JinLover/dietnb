import argparse
import logging
import shutil
import sys
from pathlib import Path
from typing import Optional
import os # For path joining

# Ensure this path is correct for your project structure
# DIETNB_STARTUP_SCRIPT_CONTENT will be read from the _startup.py file directly

logger = logging.getLogger(__name__)

def find_ipython_startup_dir() -> Optional[Path]:
    """Finds the default IPython profile's startup directory."""
    try:
        from IPython.paths import get_ipython_dir
        ip_dir = Path(get_ipython_dir())
        profile_dir = ip_dir / 'profile_default'
        startup_dir = profile_dir / 'startup'
        return startup_dir
    except ImportError:
        logger.error("IPython is not installed. Cannot find startup directory.")
        return None
    except Exception as e:
        logger.error(f"Error finding IPython startup directory: {e}")
        return None

def get_ipython_dir() -> str:
    """Returns the IPython directory path."""
    from IPython.paths import get_ipython_dir as ip_get_ipython_dir
    return ip_get_ipython_dir()

def install_startup_script():
    """Installs the dietnb startup script for IPython."""
    try:
        ipython_dir_str = get_ipython_dir()
        if not ipython_dir_str: # Should not happen if IPython is installed
            raise ImportError("IPython directory not found.")
            
        ipython_dir = Path(ipython_dir_str)
        startup_dir = ipython_dir / "profile_default" / "startup"
        startup_dir.mkdir(parents=True, exist_ok=True)
        
        # Path to the _startup.py file within the dietnb package
        # __file__ is the path to the current file (_cli.py)
        # .parent gives the directory of _cli.py (dietnb/dietnb/)
        # then we navigate to _startup.py
        source_startup_script_path = Path(__file__).parent / "_startup.py"

        if not source_startup_script_path.is_file():
            logger.error(f"Source startup script not found at {source_startup_script_path}")
            print(f"Error: Source startup script not found. Installation failed.")
            return
            
        script_name = "00-dietnb.py" # Ensure it runs early
        target_script_path = startup_dir / script_name
        
        # Read content from source and write to target
        with open(source_startup_script_path, "r") as src_f, open(target_script_path, "w") as dest_f:
            dest_f.write(src_f.read())
        
        print(f"dietnb startup script installed to: {target_script_path}")
        print("Please restart your IPython/Jupyter kernel for changes to take effect.")
        print("dietnb will now attempt to activate automatically.")
        print("If you need to specify a folder_prefix, please use manual activation:")
        print("  import dietnb; dietnb.activate(folder_prefix=\"MyProject\")")
        logger.info(f"Startup script '{script_name}' written to '{startup_dir}' from '{source_startup_script_path}'.")

    except ImportError:
        print("IPython is not installed or not found. Cannot install startup script.")
        logger.error("IPython not found, cannot install startup script.")
    except Exception as e:
        print(f"Error installing dietnb startup script: {e}")
        logger.error(f"Failed to install startup script: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="dietnb command line utility.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Install command
    parser_install = subparsers.add_parser('install', help='Install the IPython startup script for automatic activation.')
    parser_install.set_defaults(func=install_startup_script)

    # Basic logging setup for CLI
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    args = parser.parse_args()

    if hasattr(args, 'func'):
        success = args.func()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 