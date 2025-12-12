import sys
from pathlib import Path

p_dir = Path(__file__).parent
sys.path.insert(0, str(p_dir.parent))

from test_capsules import TestCapsulesAPI

test_instance = TestCapsulesAPI()
test_instance.test_browse_capsules_map_mode()