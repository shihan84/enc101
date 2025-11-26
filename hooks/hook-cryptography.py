"""
PyInstaller hook for cryptography
Ensures all cryptography modules and binaries are included
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

# Collect all cryptography submodules
hiddenimports = collect_submodules('cryptography')

# cffi is required by cryptography
hiddenimports += ['cffi', '_cffi_backend']

# Collect cryptography data files (certificates, etc.)
datas = collect_data_files('cryptography')

# Collect dynamic libraries (DLLs, .so files)
binaries = collect_dynamic_libs('cryptography')

# Also collect cffi binaries if needed
try:
    cffi_binaries = collect_dynamic_libs('cffi')
    if cffi_binaries:
        binaries += cffi_binaries
except Exception:
    pass

