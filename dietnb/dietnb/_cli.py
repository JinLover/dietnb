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
    """Copies the startup script to the IPython startup directory."""
    startup_dir = find_ipython_startup_dir()
    if not startup_dir:
        print("Could not find IPython startup directory. Installation failed.", file=sys.stderr)
        return False

    try:
        startup_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating startup directory {startup_dir}: {e}", file=sys.stderr)
        return False

    # Use importlib.resources in Python 3.9+ for robustness
    source_path = None
    try:
        if sys.version_info >= (3, 9):
            import importlib.resources as pkg_resources
            with pkg_resources.path('dietnb', '_startup.py') as p:
                source_path = p
        else:
            # Fallback for older Python versions (less robust)
            import pkg_resources
            source_path = Path(pkg_resources.resource_filename('dietnb', '_startup.py'))

    except (ImportError, ModuleNotFoundError):
         print("Could not locate the startup script within the package.", file=sys.stderr)
         # Basic fallback assuming standard package structure
         try:
             source_path = Path(__file__).parent / '_startup.py'
             if not source_path.exists():
                 raise FileNotFoundError
         except (NameError, FileNotFoundError):
              print("Fallback failed. Could not find _startup.py.", file=sys.stderr)
              return False
    except Exception as e:
         print(f"Error accessing package resources: {e}", file=sys.stderr)
         return False

    if not source_path or not source_path.exists():
         print(f"Startup script source ('{source_path}') not found. Installation failed.", file=sys.stderr)
         return False

    # Use a filename that's unlikely to clash and indicates the package
    target_filename = "99-dietnb_startup.py"
    target_path = startup_dir / target_filename

    try:
        shutil.copyfile(source_path, target_path)
        print(f"Successfully installed dietnb startup script to:\n  {target_path}")
        print("Restart your IPython kernel for changes to take effect.")
        return True
    except Exception as e:
        print(f"Error copying startup script from {source_path} to {target_path}: {e}", file=sys.stderr)
        return False

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