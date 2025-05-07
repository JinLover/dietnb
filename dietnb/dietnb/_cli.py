import argparse
import logging
import shutil
import sys
from pathlib import Path
from typing import Optional

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

def install_startup_script():
    """Installs the dietnb startup script for IPython."""
    # --- MODIFIED: Disable automatic installation --- 
    print("'dietnb install' is currently disabled.")
    print("Please activate dietnb manually in each notebook using:")
    print("  import dietnb; dietnb.activate()")
    print("or")
    print("  %load_ext dietnb")
    print("(Automatic startup script installation is not supported in this version.)")
    # --- End Modification ---

    # --- Original Code (Commented Out) ---
    # try:
    #     ipython_dir = Path(get_ipython_dir())
    #     startup_dir = ipython_dir / "profile_default" / "startup"
    #     startup_dir.mkdir(parents=True, exist_ok=True)
    # 
    #     source_path = Path(__file__).parent / "_startup.py"
    #     target_path = startup_dir / "99-dietnb.py"
    # 
    #     with source_path.open("r") as source_file, target_path.open("w") as target_file:
    #         target_file.write(source_file.read())
    #         
    #     print(f"dietnb startup script installed to: {target_path}")
    #     print("Restart your IPython kernel for changes to take effect.")
    # except Exception as e:
    #     print(f"Error installing startup script: {e}", file=sys.stderr)
    #     print("Please activate manually using 'import dietnb; dietnb.activate()' or '%load_ext dietnb'.", file=sys.stderr)
    #     sys.exit(1)
    # --- End Original Code ---

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