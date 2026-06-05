#!/usr/bin/env python3
"""
NetPulse Agent — Cross-Platform Build Script

Builds a standalone executable using PyInstaller.
Output:  dist/netpulse  (or netpulse.exe on Windows)

Usage:
    cd agent
    python build.py

Requirements:
    pip install pyinstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def main():
    root = Path(__file__).parent.resolve()
    spec_file = root / 'netpulse.spec'
    dist_dir = root / 'dist'
    build_dir = root / 'build'

    print(f'NetPulse Agent Builder')
    print(f'{"=" * 40}')
    print(f'Platform: {sys.platform}')
    print(f'Python:   {sys.version}')
    print()

    if not shutil.which('pyinstaller'):
        print('Error: PyInstaller not found.')
        print('Install with: pip install pyinstaller')
        sys.exit(1)

    if build_dir.exists():
        print(f'Cleaning build directory...')
        shutil.rmtree(build_dir)

    print(f'Building executable from: {spec_file}')
    print()

    result = subprocess.run(
        [sys.executable, '-m', 'PyInstaller', str(spec_file), '--clean', '--noconfirm'],
        cwd=root,
        capture_output=False,
    )

    if result.returncode != 0:
        print(f'\nBuild failed with exit code {result.returncode}')
        sys.exit(result.returncode)

    print()
    print(f'Build complete!')
    print()

    exe_name = 'netpulse.exe' if sys.platform == 'win32' else 'netpulse'
    exe_path = dist_dir / exe_name

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f'Executable: {exe_path} ({size_mb:.1f} MB)')
        print(f'Run:        {exe_path}')
    elif dist_dir.exists():
        print(f'Output directory: {dist_dir}')
        print(f'Contents: {list(dist_dir.iterdir())}')

    print()
    print('Note: network scanning requires root/admin privileges.')
    print('Run with sudo on Linux/Mac or as Administrator on Windows.')


if __name__ == '__main__':
    main()
