"""
PyInstaller runtime hook to handle pkg_resources gracefully
Prevents Lorem ipsum.txt and other setuptools resource errors

This hook runs early in the PyInstaller boot process to patch pkg_resources
before any other code tries to use it.
"""

import sys
import warnings
from io import BytesIO

# Suppress pkg_resources warnings about missing resources
warnings.filterwarnings('ignore', message='.*Lorem ipsum.*')
warnings.filterwarnings('ignore', category=UserWarning, module='pkg_resources')

# Pre-emptively patch pkg_resources functions before they're used
try:
    import pkg_resources

    # Store original functions
    _original_resource_stream = pkg_resources.resource_stream
    _original_resource_string = pkg_resources.resource_string
    _original_resource_filename = pkg_resources.resource_filename


    def patched_resource_stream(package_or_requirement, resource_name):
        """Patched resource_stream that fails gracefully"""
        try:
            return _original_resource_stream(package_or_requirement, resource_name)
        except (FileNotFoundError, KeyError, OSError) as e:
            # If resource not found, check if it's a known problematic resource
            if 'Lorem ipsum' in resource_name or 'jaraco' in str(package_or_requirement):
                # For jaraco.text Lorem ipsum, return empty bytes stream
                return BytesIO(b'')
            # For other resources, re-raise the error
            raise


    def patched_resource_string(package_or_requirement, resource_name):
        """Patched resource_string that fails gracefully"""
        try:
            return _original_resource_string(package_or_requirement, resource_name)
        except (FileNotFoundError, KeyError, OSError) as e:
            # If resource not found, check if it's a known problematic resource
            if 'Lorem ipsum' in resource_name or 'jaraco' in str(package_or_requirement):
                # For jaraco.text Lorem ipsum, return empty bytes
                return b''
            # For other resources, re-raise the error
            raise


    def patched_resource_filename(package_or_requirement, resource_name):
        """Patched resource_filename that fails gracefully"""
        try:
            return _original_resource_filename(package_or_requirement, resource_name)
        except (FileNotFoundError, KeyError, OSError) as e:
            # If resource not found, check if it's a known problematic resource
            if 'Lorem ipsum' in resource_name or 'jaraco' in str(package_or_requirement):
                # For jaraco.text Lorem ipsum, return a dummy path
                # (caller typically just reads the file, so they'll get empty content)
                import tempfile
                import os
                # Create a temporary empty file
                fd, path = tempfile.mkstemp(suffix='.txt')
                os.close(fd)
                return path
            # For other resources, re-raise the error
            raise


    # Apply the patches
    pkg_resources.resource_stream = patched_resource_stream
    pkg_resources.resource_string = patched_resource_string
    pkg_resources.resource_filename = patched_resource_filename

except ImportError:
    # pkg_resources not available, nothing to patch
    pass
except Exception as e:
    # If patching fails, log it but don't crash
    print(f"Warning: Could not patch pkg_resources: {e}", file=sys.stderr)
