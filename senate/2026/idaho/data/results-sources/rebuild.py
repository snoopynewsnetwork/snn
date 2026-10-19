#!/usr/bin/env python3
"""Offline deterministic replay of derived research records; --check is read-only."""
import os,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
runpy.run_path(str(Path(__file__).with_name('build.py')),run_name='__main__')
