"""Test configuration for pytest."""

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.absolute()

sys.path.insert(0, str(root_dir))
